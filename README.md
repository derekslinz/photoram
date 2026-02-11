# photoram

A modern CLI photo tagger powered by **RAM++** (Recognize Anything Model Plus Plus). Offline image tagging with state-of-the-art accuracy — a spiritual successor to [photils-cli](https://github.com/scheckmedia/photils-cli).

## Features

- **4,585+ tag vocabulary** — RAM++ recognizes thousands of common + open-set categories
- **Fully offline** — no data leaves your machine
- **Batch inference** — process images in GPU-accelerated batches with `--batch-size`
- **Batch processing** — tag entire directories recursively
- **Confidence scores** — see how confident the model is per tag
- **EXIF/XMP/IPTC metadata writing** — embed tags directly into image files
- **Tag translation/override** — customize tags via a simple JSON mapping
- **Multiple output formats** — text, JSON, CSV
- **GPU accelerated** — CUDA & Apple MPS support with automatic fallback to CPU
- **Auto model download** — fetches the RAM++ checkpoint from HuggingFace on first run
- **Input validation** — clear error messages with standardized exit codes
- **Service layer architecture** — clean separation of CLI, orchestration, and model concerns

## Installation

```bash
# Basic install
pip install -e .

# With metadata writing support
pip install -e ".[metadata]"

# With dev/test dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Tag a single image
photoram tag photo.jpg

# Tag with confidence scores
photoram tag photo.jpg --confidence

# Tag all images in a directory
photoram tag ./photos/ --recursive

# Write tags into image EXIF/XMP metadata
photoram tag photo.jpg --write-metadata

# Output as JSON (always returns a list)
photoram tag photo.jpg --format json

# Adjust detection threshold (default: 0.68)
photoram tag photo.jpg --threshold 0.6

# Batch inference for faster GPU processing
photoram tag ./photos/ --recursive --batch-size 8

# Limit number of tags
photoram tag photo.jpg --top-n 10

# Use tag overrides/translations
photoram tag photo.jpg --overrides my_overrides.json
```

## Output Contract

### JSON Format

JSON output **always returns a list** (array), even for a single image:

```json
[
  {
    "file": "photo.jpg",
    "tags": ["tree", "sky", "mountain"],
    "confidences": [0.95, 0.88, 0.72]
  }
]
```

With `--confidence` flag, confidences are included. With `--chinese`, Chinese tags are added:

```json
[
  {
    "file": "photo.jpg",
    "tags": ["tree", "sky"],
    "confidences": [0.95, 0.88],
    "tags_chinese": ["树", "天空"]
  }
]
```

### Text Format

Single image (photils-cli compatible): pipe-separated tags on one line.

```text
tree | sky | mountain | building
```

Multiple images: tab-separated file path and tags.

### CSV Format

Standard CSV with `file` and `tags` columns (optionally `confidences`, `tags_chinese`).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No images found |
| 2 | Invalid arguments (threshold, top-n, batch-size, etc.) |
| 3 | Model error (download, corruption, inference) |
| 4 | Other runtime error |

## Tag Translation

Create an `override_labels.json` file to rename or translate tags:

```json
{
    "blackbackground": "black background",
    "art": "kunst",
    "shadow": "schatten"
}
```

Place it at `~/.config/photoram/override_labels.json` or pass it with `--overrides`.

## CLI Reference

```text
photoram tag [OPTIONS] INPUT...

Arguments:
  INPUT                  Image file(s) or directory to tag

Options:
  -t, --threshold FLOAT    Detection threshold 0.0–1.0 (default: 0.68)
  -n, --top-n INTEGER      Maximum number of tags to return
  -c, --confidence         Show confidence scores
  -f, --format FORMAT      Output format: text, json, csv (default: text)
  -o, --output FILE        Write results to file
  -r, --recursive          Recursively scan directories
  -w, --write-metadata     Write tags to image EXIF/XMP/IPTC metadata
      --overrides FILE     Tag override/translation JSON file
      --device DEVICE      Force device: cpu, cuda, mps (default: auto)
      --image-size INT     Input image size (default: 384)
      --batch-size INT     Images per inference batch (default: 1)
      --chinese            Also output Chinese tags
  -q, --quiet              Suppress progress output
  -h, --help               Show this help message
```

## Architecture

```
CLI (cli.py)
 └─ TaggingService (service.py)     ← orchestration layer
     ├─ RAMPlusModel (model.py)     ← model loading & inference
     ├─ utils.py                    ← file discovery, overrides, formatting
     └─ schemas.py                  ← TagResult, BatchResult
```

- **`cli.py`** — Click interface, output formatting, exit code handling
- **`service.py`** — Decouples CLI from inference; owns model lifecycle, image collection, post-processing
- **`model.py`** — RAM++ model loading, checkpoint management, single & batch inference
- **`schemas.py`** — Typed result schemas (`TagResult`, `BatchResult`) used by all output writers
- **`errors.py`** — Standardized exit codes and exception hierarchy
- **`metadata.py`** — EXIF/XMP/IPTC writing via exiftool or pyexiv2
- **`utils.py`** — Tag overrides, file discovery, text formatting

## Supported Formats

**Input:** JPEG, PNG, TIFF, BMP, WebP, HEIC, GIF (any format PIL can read)

**Output:** Text (pipe-separated), JSON, CSV

## How It Works

photoram uses the [RAM++ (Recognize Anything Plus Plus)](https://github.com/xinyu1205/recognize-anything) model — a state-of-the-art vision transformer that was trained on millions of image-tag-text triplets. On first run, the model weights (~2.8 GB) are automatically downloaded from HuggingFace.

## darktable Integration

photoram is designed as a drop-in replacement for photils-cli. To use with the [photils-dt](https://github.com/scheckmedia/photils-dt) darktable plugin, configure it to call:

```bash
photoram tag --image "$FILE"
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=photoram
```

## License

MIT
