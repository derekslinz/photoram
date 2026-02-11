"""Tests for photoram.model image-size normalization safeguards."""

from __future__ import annotations

import warnings

from photoram.model import DEFAULT_IMAGE_SIZE, RAMPlusModel


def test_resolve_ram_image_size_allows_supported_values() -> None:
    assert RAMPlusModel._resolve_ram_image_size(224) == 224
    assert RAMPlusModel._resolve_ram_image_size(384) == 384


def test_resolve_ram_image_size_falls_back_for_unsupported_values() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        resolved = RAMPlusModel._resolve_ram_image_size(512)

    assert resolved == DEFAULT_IMAGE_SIZE
    assert any("vision_config_path" in str(w.message) for w in caught)
