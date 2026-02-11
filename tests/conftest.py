"""Shared test fixtures for photoram."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """A temporary directory for test artifacts."""
    return tmp_path


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a minimal valid PNG file for testing."""
    # 1x1 red pixel PNG
    import struct
    import zlib

    def _create_png(width: int = 1, height: int = 1) -> bytes:
        def _chunk(chunk_type: bytes, data: bytes) -> bytes:
            c = chunk_type + data
            crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
            return struct.pack(">I", len(data)) + c + crc

        header = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        raw = b""
        for _ in range(height):
            raw += b"\x00" + b"\xff\x00\x00" * width
        idat = zlib.compress(raw)
        return header + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")

    img = tmp_path / "test_image.png"
    img.write_bytes(_create_png())
    return img


@pytest.fixture
def sample_images(tmp_path: Path, sample_image: Path) -> list[Path]:
    """Create multiple test images."""
    import shutil

    images = [sample_image]
    for i in range(1, 4):
        dest = tmp_path / f"test_image_{i}.png"
        shutil.copy(sample_image, dest)
        images.append(dest)
    return images


@pytest.fixture
def override_file(tmp_path: Path) -> Path:
    """Create a sample override JSON file."""
    overrides = {"tree": "baum", "sky": "himmel", "dog": "hund"}
    path = tmp_path / "overrides.json"
    path.write_text(json.dumps(overrides), encoding="utf-8")
    return path


@pytest.fixture
def non_image_file(tmp_path: Path) -> Path:
    """Create a non-image file."""
    f = tmp_path / "notes.txt"
    f.write_text("not an image", encoding="utf-8")
    return f
