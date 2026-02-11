"""Write tags into image EXIF/XMP/IPTC metadata.

Diagnostics:
  • Failures are reported per-image but never abort the batch.
  • Both exiftool and pyexiv2 paths raise MetadataWriteError with
    actionable remediation messages.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .errors import MetadataWriteError


def _has_exiftool() -> bool:
    return shutil.which("exiftool") is not None


def write_metadata_exiftool(image_path: str | Path, tags: list[str]) -> None:
    """Write tags to IPTC:Keywords and XMP:Subject using exiftool."""
    if not _has_exiftool():
        raise MetadataWriteError(
            "exiftool is not installed. Install it with:\n"
            "  macOS:  brew install exiftool\n"
            "  Linux:  sudo apt install libimage-exiftool-perl"
        )

    args = ["exiftool", "-overwrite_original"]
    for tag in tags:
        args.append(f"-IPTC:Keywords={tag}")
        args.append(f"-XMP:Subject={tag}")
    # `--` prevents filenames beginning with '-' from being parsed as options.
    args.append("--")
    args.append(str(image_path))

    try:
        result = subprocess.run(args, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        raise MetadataWriteError(
            "exiftool was found on PATH but failed to execute.\n"
            "Ensure exiftool is installed correctly."
        )

    if result.returncode != 0:
        raise MetadataWriteError(
            f"exiftool failed on {image_path}:\n"
            f"  stderr: {result.stderr.strip()}\n"
            f"  exit code: {result.returncode}"
        )


def write_metadata_pyexiv2(image_path: str | Path, tags: list[str]) -> None:
    """Write tags to IPTC and XMP using pyexiv2 (no external dependency)."""
    try:
        import pyexiv2  # type: ignore[import-untyped]
    except ImportError:
        raise MetadataWriteError(
            "pyexiv2 is not installed. Install with:\n"
            '  pip install "photoram[metadata]"'
        ) from None

    try:
        with pyexiv2.Image(str(image_path)) as img:
            # IPTC keywords
            img.modify_iptc({"Iptc.Application2.Keywords": tags})
            # XMP subject
            img.modify_xmp({"Xmp.dc.subject": tags})
    except Exception as e:
        raise MetadataWriteError(
            f"pyexiv2 failed writing metadata to {image_path}:\n"
            f"  {e}\n"
            f"Image file was NOT modified."
        ) from e


def write_metadata(image_path: str | Path, tags: list[str]) -> None:
    """Write tags using the best available method.

    Prefers exiftool (more robust), falls back to pyexiv2.
    Raises MetadataWriteError with diagnostics on any failure.
    """
    if _has_exiftool():
        write_metadata_exiftool(image_path, tags)
    else:
        write_metadata_pyexiv2(image_path, tags)
