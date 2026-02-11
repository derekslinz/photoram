"""Write tags into image EXIF/XMP/IPTC metadata."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _has_exiftool() -> bool:
    return shutil.which("exiftool") is not None


def write_metadata_exiftool(image_path: str | Path, tags: list[str]) -> None:
    """Write tags to IPTC:Keywords and XMP:Subject using exiftool."""
    if not _has_exiftool():
        raise RuntimeError(
            "exiftool is not installed. Install it with:\n"
            "  macOS:  brew install exiftool\n"
            "  Linux:  sudo apt install libimage-exiftool-perl\n"
        )

    args = ["exiftool", "-overwrite_original"]
    for tag in tags:
        args.append(f"-IPTC:Keywords={tag}")
        args.append(f"-XMP:Subject={tag}")
    args.append(str(image_path))

    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"exiftool failed: {result.stderr.strip()}")


def write_metadata_pyexiv2(image_path: str | Path, tags: list[str]) -> None:
    """Write tags to IPTC and XMP using pyexiv2 (no external dependency)."""
    try:
        import pyexiv2  # type: ignore[import-untyped]
    except ImportError:
        raise RuntimeError(
            "pyexiv2 is not installed. Install with:\n"
            '  pip install "photoram[metadata]"\n'
        ) from None

    with pyexiv2.Image(str(image_path)) as img:
        # IPTC keywords
        img.modify_iptc({"Iptc.Application2.Keywords": tags})
        # XMP subject
        img.modify_xmp({"Xmp.dc.subject": tags})


def write_metadata(image_path: str | Path, tags: list[str]) -> None:
    """Write tags using the best available method.

    Prefers exiftool (more robust), falls back to pyexiv2.
    """
    if _has_exiftool():
        write_metadata_exiftool(image_path, tags)
    else:
        write_metadata_pyexiv2(image_path, tags)
