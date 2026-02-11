"""Tag override/translation and output formatting utilities."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Config paths
# ---------------------------------------------------------------------------

CONFIG_DIR = Path(os.environ.get(
    "PHOTORAM_CONFIG",
    Path.home() / ".config" / "photoram",
))

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tiff", ".tif",
    ".bmp", ".webp", ".heic", ".heif", ".gif",
}


# ---------------------------------------------------------------------------
# Tag overrides
# ---------------------------------------------------------------------------

def load_overrides(path: Optional[str | Path] = None) -> dict[str, str]:
    """Load a tag-name override/translation map from JSON.

    Lookup order:
      1. Explicit *path* argument
      2. ``~/.config/photoram/override_labels.json``
    """
    candidates: list[Path] = []
    if path:
        candidates.append(Path(path))
    candidates.append(CONFIG_DIR / "override_labels.json")

    for p in candidates:
        if p.is_file():
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    return {}


def apply_overrides(
    tags: list[str],
    overrides: dict[str, str],
) -> list[str]:
    """Return a new tag list with overrides applied."""
    if not overrides:
        return tags
    return [overrides.get(t, t) for t in tags]


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def collect_images(
    inputs: tuple[str, ...],
    recursive: bool = False,
) -> list[Path]:
    """Resolve a mixed list of files/directories into image paths."""
    result: list[Path] = []
    for inp in inputs:
        p = Path(inp)
        if p.is_file():
            if p.suffix.lower() in IMAGE_EXTENSIONS:
                result.append(p)
        elif p.is_dir():
            pattern = "**/*" if recursive else "*"
            for child in sorted(p.glob(pattern)):
                if child.is_file() and child.suffix.lower() in IMAGE_EXTENSIONS:
                    result.append(child)
    return result


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_tags_text(
    tags: list[str],
    confidences: Optional[list[float]] = None,
    show_confidence: bool = False,
) -> str:
    """Pipe-separated tag string, optionally with confidence."""
    if show_confidence and confidences:
        return " | ".join(
            f"{t} ({c:.2%})" for t, c in zip(tags, confidences)
        )
    return " | ".join(tags)


def format_result_json(
    path: str,
    tags: list[str],
    confidences: list[float],
) -> dict:
    """Return a JSON-serializable dict for one image."""
    d: dict = {
        "file": path,
        "tags": tags,
        "confidences": confidences,
    }
    return d
