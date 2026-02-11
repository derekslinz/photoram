"""Extract all RAM++ tags to tags.json."""
import json
from pathlib import Path

ram_data = Path(".venv/lib/python3.9/site-packages/ram/data")

with open(ram_data / "ram_tag_list.txt", encoding="utf-8") as f:
    tags_en = [line.strip() for line in f if line.strip()]
with open(ram_data / "ram_tag_list_chinese.txt", encoding="utf-8") as f:
    tags_zh = [line.strip() for line in f if line.strip()]
with open(ram_data / "ram_tag_list_threshold.txt", encoding="utf-8") as f:
    thresholds = [float(line.strip()) for line in f if line.strip()]

tag_list = []
for i in range(len(tags_en)):
    entry = {
        "id": i,
        "tag": tags_en[i],
        "tag_chinese": tags_zh[i] if i < len(tags_zh) else "",
        "threshold": thresholds[i] if i < len(thresholds) else 0.5,
    }
    tag_list.append(entry)

output = {
    "model": "RAM++ (recognize-anything-plus-model)",
    "source": "xinyu1205/recognize-anything-plus-model",
    "total_tags": len(tag_list),
    "description": "Complete vocabulary of tags recognized by RAM++. Each entry includes the English tag, Chinese translation, per-class calibrated threshold, and internal index.",
    "tags": tag_list,
}

with open("tags.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Created tags.json with {len(tag_list)} tags")
