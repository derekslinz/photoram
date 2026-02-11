--[[
  photoram darktable plugin (multi-image auto-tagging)

  Features:
  - Handles multiple selected images in one invocation
  - Exposes core photoram-cli parameters via darktable preferences
  - Attaches generated tags directly to selected images in darktable

  Install:
  1. Copy this file to ~/.config/darktable/lua/photoram.lua
  2. Add to ~/.config/darktable/luarc:
       require "photoram"
  3. Restart darktable

  Usage:
  - In lighttable, select one or more images
  - Use selected images action: "photoram auto-tag"
]]

local dt = require "darktable"

local MODULE = "photoram"
local PS = dt.configuration.running_os == "windows" and "\\" or "/"

local gettext = dt.gettext.gettext
local function _(msgid)
  return gettext(msgid)
end

local function shell_quote(arg)
  arg = tostring(arg or "")
  if dt.configuration.running_os == "windows" then
    return '"' .. arg:gsub('"', '\\"') .. '"'
  end
  return "'" .. arg:gsub("'", "'\\''") .. "'"
end

local function image_path(image)
  return image.path .. PS .. image.filename
end

local function trim(s)
  return (s:gsub("^%s+", ""):gsub("%s+$", ""))
end

local function split_tags(tags_field)
  local tags = {}
  if not tags_field or tags_field == "" then
    return tags
  end

  for token in tags_field:gmatch("([^|]+)") do
    local t = trim(token)
    if t ~= "" then
      table.insert(tags, t)
    end
  end

  return tags
end

local function parse_photoram_text_output(output_file, selected_count, fallback_single_path)
  local result = {}

  for line in io.lines(output_file) do
    if line ~= "" then
      local file_path, tags_field = line:match("^(.-)\t(.*)$")
      if file_path then
        result[file_path] = split_tags(tags_field)
      elseif selected_count == 1 and fallback_single_path then
        -- Single-image text format prints only tags.
        result[fallback_single_path] = split_tags(line)
      end
    end
  end

  return result
end

local function read_file(path)
  local f = io.open(path, "r")
  if not f then
    return ""
  end
  local content = f:read("*a") or ""
  f:close()
  return content
end

local function pref_string(key, default)
  local v = dt.preferences.read(MODULE, key, "string")
  if v == nil or v == "" then
    return default
  end
  return v
end

local function pref_int(key, default, min_value)
  local v = tonumber(dt.preferences.read(MODULE, key, "integer"))
  if v == nil then
    return default
  end
  v = math.floor(v)
  if min_value and v < min_value then
    return min_value
  end
  return v
end

local function pref_bool(key, default)
  local v = dt.preferences.read(MODULE, key, "bool")
  if v == nil then
    return default
  end
  return v
end

local function resolve_images(images)
  if images and #images > 0 then
    return images
  end
  if dt.gui and dt.gui.action_images and #dt.gui.action_images > 0 then
    return dt.gui.action_images
  end
  if dt.gui and dt.gui.selection and #dt.gui.selection() > 0 then
    return dt.gui.selection()
  end
  return {}
end

local function execute_command(command)
  if dt.control and dt.control.execute then
    return dt.control.execute(command)
  end

  -- Fallback for older darktable/Lua environments.
  local ok, _, code = os.execute(command)
  if ok == true then
    return 0
  end
  if type(code) == "number" then
    return code
  end
  return 1
end

local function run_photoram(images)
  images = resolve_images(images)
  if not images or #images == 0 then
    dt.print(_("photoram: no images selected"))
    return
  end

  local executable = pref_string("binary_path", "photoram-cli")
  local max_tags = pref_int("max_tags", 10, 1)
  local threshold_pct = pref_int("threshold_percent", 80, 0)
  if threshold_pct > 100 then threshold_pct = 100 end
  local batch_size = pref_int("batch_size", 32, 1)
  local write_metadata = pref_bool("write_metadata", false)

  local threshold = threshold_pct / 100.0

  local selected_paths = {}
  for _, image in ipairs(images) do
    table.insert(selected_paths, image_path(image))
  end

  local tmp_out = os.tmpname()
  local tmp_err = os.tmpname()

  local cmd_parts = {
    shell_quote(executable),
    "tag",
    "--quiet",
    "--format", "text",
    "--top-n", tostring(max_tags),
    "--threshold", string.format("%.2f", threshold),
    "--batch-size", tostring(batch_size),
  }

  if write_metadata then
    table.insert(cmd_parts, "--write-metadata")
  end

  for _, path in ipairs(selected_paths) do
    table.insert(cmd_parts, shell_quote(path))
  end

  local command = table.concat(cmd_parts, " ")
    .. " > " .. shell_quote(tmp_out)
    .. " 2> " .. shell_quote(tmp_err)

  local ret = execute_command(command)
  if ret ~= 0 then
    local stderr = read_file(tmp_err)
    os.remove(tmp_out)
    os.remove(tmp_err)

    dt.print_error(string.format(_("photoram failed with exit code %d"), ret))
    if stderr ~= "" then
      local first_line = stderr:match("([^\n]+)") or stderr
      dt.print_error(first_line)
    end
    return
  end

  local tag_map = parse_photoram_text_output(tmp_out, #images, selected_paths[1])
  os.remove(tmp_out)
  os.remove(tmp_err)

  local tagged_images = 0
  local attached_tags = 0

  for _, image in ipairs(images) do
    local path = image_path(image)
    local tags = tag_map[path]

    if tags and #tags > 0 then
      local local_seen = {}
      local added_for_image = 0

      for _, tag in ipairs(tags) do
        if not local_seen[tag] then
          local_seen[tag] = true
          dt.tags.attach(dt.tags.create(tag), image)
          added_for_image = added_for_image + 1
          attached_tags = attached_tags + 1
        end
      end

      if added_for_image > 0 then
        tagged_images = tagged_images + 1
      end
    end
  end

  dt.print(string.format(
    _("photoram: tagged %d/%d images (%d tags attached)"),
    tagged_images,
    #images,
    attached_tags
  ))
end

local action_registered = false
local shortcut_registered = false

local function destroy()
  if action_registered then
    pcall(function()
      dt.gui.libs.image.destroy_action(MODULE)
    end)
    action_registered = false
  end

  if shortcut_registered then
    pcall(function()
      dt.destroy_event(MODULE, "shortcut")
    end)
    shortcut_registered = false
  end
end

local ok_action, err_action = pcall(function()
  dt.gui.libs.image.register_action(
    MODULE,
    _("photoram auto-tag"),
    function(event, images)
      run_photoram(images)
    end,
    _("Run photoram-cli on selected images and attach predicted tags")
  )
  action_registered = true
end)
if not ok_action then
  dt.print_error(_("photoram: failed to register image action"))
  dt.print_log("photoram action registration error: " .. tostring(err_action))
end

local ok_shortcut, err_shortcut = pcall(function()
  dt.register_event(
    MODULE,
    "shortcut",
    function(event, shortcut)
      run_photoram(dt.gui.action_images)
    end,
    _("photoram auto-tag")
  )
  shortcut_registered = true
end)
if not ok_shortcut then
  dt.print_log("photoram shortcut registration error: " .. tostring(err_shortcut))
end

-- Preferences
local function safe_register_pref(name, pref_type, label, tooltip, default)
  local ok, err = pcall(function()
    dt.preferences.register(MODULE, name, pref_type, label, tooltip, default)
  end)
  if not ok then
    dt.print_log("photoram preference registration error (" .. name .. "): " .. tostring(err))
  end
end

safe_register_pref(
  "binary_path",
  "string",
  _("photoram: executable"),
  _("Path or command name for photoram-cli. Requires restart to take effect."),
  "photoram-cli"
)

safe_register_pref(
  "max_tags",
  "integer",
  _("photoram: max tags"),
  _("Maximum number of tags per image (--top-n)."),
  10
)

safe_register_pref(
  "threshold_percent",
  "integer",
  _("photoram: threshold (%)"),
  _("Confidence threshold in percent (maps to --threshold)."),
  80
)

safe_register_pref(
  "batch_size",
  "integer",
  _("photoram: batch size"),
  _("Images processed per inference batch (--batch-size)."),
  32
)

safe_register_pref(
  "write_metadata",
  "bool",
  _("photoram: write metadata"),
  _("Also write predicted tags to image metadata via photoram-cli."),
  false
)

local script_data = {}
script_data.metadata = {
  name = _("photoram"),
  purpose = _("auto-tag selected images with photoram-cli"),
  author = "photoram",
  help = "https://github.com/lderek/photoram",
}
script_data.destroy = destroy

return script_data
