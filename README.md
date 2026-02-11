# photoram

`photoram` is a CLI photo tagger powered by RAM++ (Recognize Anything Model Plus Plus). It is designed as a modern, scriptable successor to [photils-cli](https://github.com/scheckmedia/photils-cli). The installed command is `photoram-cli`.

## Highlights

- RAM++ tagging with 4,585+ open-set labels.
- Offline inference after first-run checkpoint download.
- Batch inference (`--batch-size`) with streaming mini-batch loading.
- Stable JSON output contract: `--format json` always returns a list.
- Standardized exit codes and validation errors.
- Service-layer architecture (`TaggingService`) that decouples CLI from model internals.
- photils compatibility flags: `--image`, `--output_file`, `--with_confidence`.

## Security Hardening

- Checkpoint integrity verification: RAM++ checkpoint is SHA-256 validated before model load.
- Image safety checks: decompression-bomb protection is enabled (`PHOTORAM_MAX_IMAGE_PIXELS`, default `120000000`).
- Metadata subprocess hardening: exiftool invocation uses `--` before image path to prevent option parsing.
- Streaming batch loader: avoids preloading all tensors for large jobs.
- CI security gates: `bandit` (SAST) and `pip-audit` (dependency CVEs).

## Requirements

- Python 3.9+
- `pip`
- `git` (for source installs)

## Installation

### Local editable install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
photoram-cli --help
```

### Reproducible install (constraints)

```bash
pip install -c constraints.txt -e .
```

### Optional extras

```bash
# Metadata fallback support (pyexiv2)
pip install -e ".[metadata]"

# Dev + test + security tooling
pip install -c constraints.txt -e ".[dev]"
```

If you use `--write-metadata`, installing `exiftool` is recommended:

```bash
# macOS
brew install exiftool

# Debian/Ubuntu
sudo apt install libimage-exiftool-perl
```

## Quick Start

```bash
# Tag one image
photoram-cli tag photo.jpg

# Include confidence scores
photoram-cli tag photo.jpg --confidence

# Recursive directory tagging
photoram-cli tag ./photos --recursive

# Batch inference (faster on GPU, higher VRAM use)
photoram-cli tag ./photos --recursive --batch-size 32

# Write metadata
photoram-cli tag photo.jpg --write-metadata

# JSON output (always a list)
photoram-cli tag photo.jpg --format json

# Print timing summary (model load, tagging, total)
photoram-cli tag photo.jpg -T

# Show environment/model cache info
photoram-cli info
```

Note: first run requires internet access to download the RAM++ checkpoint into the local cache.

## Commands

### `photoram-cli tag`

```text
photoram-cli tag [OPTIONS] INPUT...

Arguments:
  INPUT                  Image file(s) or directory to tag

Options:
  -t, --threshold FLOAT  Detection threshold 0.0-1.0 (default: 0.8)
  -n, --top-n INTEGER    Maximum number of tags to return
  -c, --confidence       Show confidence scores
  -f, --format FORMAT    Output format: text, json, csv (default: json)
  -o, --output FILE      Write results to file
  -r, --recursive        Recursively scan directories
  -w, --write-metadata   Write tags to image EXIF/XMP/IPTC metadata
      --overrides FILE   Tag override/translation JSON file
      --batch-size INT   Images per inference batch (default: 32)
  -T, --timings          Print basic timings (load, tagging, total)
  -q, --quiet            Suppress progress output
  -h, --help             Show help
```

Compatibility alias for photils-dt-style calls:

```bash
photoram-cli tag --image "$FILE"
```

### `photoram-cli info`

Prints package version, torch/runtime capability, resolved default device, and model cache information.

## darktable Lua Plugin

A multi-image darktable plugin is included at:

- `darktable/photoram.lua`

What it does:

- Works on all selected images in one action (not single-image only).
- Exposes tunable parameters in darktable preferences:
- `photoram: max tags` -> `--top-n`
- `photoram: threshold (%)` -> `--threshold`
- `photoram: batch size` -> `--batch-size`
- `photoram: write metadata` -> `--write-metadata`
- `photoram: executable` -> command/path to `photoram-cli`

Install:

```bash
mkdir -p ~/.config/darktable/lua
cp darktable/photoram.lua ~/.config/darktable/lua/photoram.lua
echo 'require "photoram"' >> ~/.config/darktable/luarc
```

Then restart darktable and run the selected-images action:

- `photoram auto-tag`

The plugin also registers a visible panel module:

- Name: `photoram auto-tagger`
- Location: right panel in lighttable (or left panel in darkroom)
- Button: `auto-tag selected`

Troubleshooting:

1. Check darktable Lua logs for load errors:
- Linux/macOS: start darktable from terminal and inspect stderr output.
2. Ensure the panel is enabled in darktable module visibility settings.
3. Confirm plugin is in the exact path:
- `~/.config/darktable/lua/photoram.lua`
4. Confirm `luarc` contains:
- `require "photoram"`
5. If `photoram-cli` is not on PATH, set preference:
- `photoram: executable` to full binary path (for example `/usr/local/bin/photoram-cli`).

## Output Contract

### JSON (`--format json`)

Always returns a list, even for one image.

```json
[
  {
    "file": "photo.jpg",
    "tags": ["tree", "sky"]
  }
]
```

- Add `--confidence` to include `confidences`.
- Failed files include an `error` field.

### Text (`--format text`)

- One image: `tag1 | tag2 | tag3`
- Multiple images: `<file>\t<tags>` per line

### CSV (`--format csv`)

- Base columns: `file`, `tags`
- Optional columns: `confidences`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No images found |
| 2 | Invalid arguments |
| 3 | Model/download/load error |
| 4 | Other runtime error |

## Tag Overrides

Create `override_labels.json`:

```json
{
  "blackbackground": "black background",
  "art": "kunst",
  "shadow": "schatten"
}
```

Lookup order:

- Explicit `--overrides <file>`
- `~/.config/photoram/override_labels.json`

## Architecture

```text
cli.py -> service.py -> model.py
                 \-> utils.py
                 \-> schemas.py
                 \-> errors.py
                 \-> metadata.py
```

- `src/photoram/cli.py`: Click commands, progress, output and exit handling.
- `src/photoram/service.py`: orchestration layer (collection, dispatch, post-processing).
- `src/photoram/model.py`: RAM++ loading, checkpoint management, inference, safety checks.
- `src/photoram/schemas.py`: result schemas (`TagResult`, `BatchResult`).
- `src/photoram/errors.py`: exception hierarchy and exit codes.
- `src/photoram/metadata.py`: metadata writing adapters.
- `src/photoram/utils.py`: file discovery, overrides, format helpers.

## Development and Tests

```bash
pip install -c constraints.txt -e ".[dev]"
pytest
```

Security scans:

```bash
bandit -q -r src
pip-audit
```

Main CLI contract tests:

- `tests/test_cli.py`
- `tests/test_cli_integration.py`

## License

MIT
