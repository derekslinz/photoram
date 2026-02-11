# photoram

`photoram` is a CLI photo tagger powered by RAM++ (Recognize Anything Model Plus Plus). It runs fully offline and is designed as a drop-in spiritual successor to [photils-cli](https://github.com/scheckmedia/photils-cli).

## New Features

- Batch inference with `--batch-size` for better GPU throughput.
- Stable JSON contract: `--format json` always returns a list.
- Standardized exit codes and clearer validation errors.
- Service-layer architecture (`TaggingService`) separating CLI and model logic.
- Expanded automated CLI coverage in `tests/test_cli.py` and `tests/test_cli_integration.py`.
- photils-cli compatibility flags: `--image`, `--output_file`, `--with_confidence`.

## Features

- 4,585+ tags from RAM++ open-set vocabulary.
- Fully offline tagging.
- Recursive directory tagging.
- Confidence scores and optional Chinese tags.
- Text, JSON, and CSV output formats.
- EXIF/XMP/IPTC metadata writing.
- Tag translation/override JSON mapping.
- CUDA and Apple MPS support with CPU fallback.
- Automatic model checkpoint download and cache validation.

## Installation

### Requirements

- Python 3.9+
- `pip`
- `git` (for source installs)

### Quick Local Install (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
photoram --help
```

### Optional Extras

```bash
# Metadata writing via pyexiv2 fallback
pip install -e ".[metadata]"

# Dev and test tools (pytest, pytest-cov)
pip install -e ".[dev]"
```

### Install as Isolated CLI with pipx

```bash
pipx install .
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
# Tag a single image
photoram tag photo.jpg

# Include confidence scores
photoram tag photo.jpg --confidence

# Tag a directory recursively
photoram tag ./photos --recursive

# Faster GPU batch inference
photoram tag ./photos --recursive --batch-size 8

# Write metadata
photoram tag photo.jpg --write-metadata

# JSON output (always a list)
photoram tag photo.jpg --format json

# Tag overrides/translations
photoram tag photo.jpg --overrides my_overrides.json
```

## Output Contract

### JSON

JSON output is always an array, even for one image.

```json
[
  {
    "file": "photo.jpg",
    "tags": ["tree", "sky"]
  }
]
```

Add `--confidence` for `confidences`, and `--chinese` for `tags_chinese`.

### Text

For one image, output is a single pipe-separated line:

```text
tree | sky | mountain
```

For multiple images, output is tab-separated: `<file>\t<tags>`.

### CSV

CSV contains `file` and `tags`, plus optional `confidences` and `tags_chinese`.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No images found |
| 2 | Invalid arguments |
| 3 | Model error |
| 4 | Other runtime error |

## Tag Translation

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

## CLI Reference

```text
photoram tag [OPTIONS] INPUT...

Arguments:
  INPUT                  Image file(s) or directory to tag

Options:
  -t, --threshold FLOAT  Detection threshold 0.0-1.0 (default: 0.68)
  -n, --top-n INTEGER    Maximum number of tags to return
  -c, --confidence       Show confidence scores
  -f, --format FORMAT    Output format: text, json, csv (default: text)
  -o, --output FILE      Write results to file
  -r, --recursive        Recursively scan directories
  -w, --write-metadata   Write tags to image EXIF/XMP/IPTC metadata
      --overrides FILE   Tag override/translation JSON file
      --device DEVICE    Force device: cpu, cuda, mps (default: auto)
      --image-size INT   Input image size (default: 384)
      --batch-size INT   Images per inference batch (default: 1)
      --chinese          Also output Chinese tags
  -q, --quiet            Suppress progress output
  -h, --help             Show help
```

Compatibility alias for photils-dt style calls:

```bash
photoram tag --image "$FILE"
```

## Architecture

```text
cli.py -> service.py -> model.py
                 \-> utils.py
                 \-> schemas.py
```

- `src/photoram/cli.py`: Click commands, formatting, exit handling.
- `src/photoram/service.py`: orchestration layer (load, collect, post-process).
- `src/photoram/model.py`: RAM++ loading, checkpoint management, inference.
- `src/photoram/schemas.py`: typed result objects (`TagResult`, `BatchResult`).
- `src/photoram/errors.py`: exception hierarchy and exit codes.
- `src/photoram/metadata.py`: metadata writing adapters.
- `src/photoram/utils.py`: file discovery, overrides, format helpers.

## Development and Testing

```bash
pip install -e ".[dev]"
pytest
pytest --cov=photoram
```

CLI contract tests live in:
- `tests/test_cli.py`
- `tests/test_cli_integration.py`

Run only the CLI-focused tests:

```bash
pytest tests/test_cli.py tests/test_cli_integration.py
```

## License

MIT
