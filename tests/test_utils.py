"""Unit tests for photoram.utils."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from photoram.utils import (
    apply_overrides,
    collect_images,
    format_tags_text,
    load_overrides,
)


# ---------------------------------------------------------------------------
# load_overrides
# ---------------------------------------------------------------------------

class TestLoadOverrides:
    def test_returns_empty_when_no_file(self, tmp_path: Path) -> None:
        result = load_overrides(tmp_path / "nonexistent.json")
        assert result == {}

    def test_loads_from_explicit_path(self, override_file: Path) -> None:
        result = load_overrides(str(override_file))
        assert result == {"tree": "baum", "sky": "himmel", "dog": "hund"}

    def test_returns_empty_when_none(self) -> None:
        # Default lookup will fail unless config file exists
        result = load_overrides(None)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# apply_overrides
# ---------------------------------------------------------------------------

class TestApplyOverrides:
    def test_no_overrides_returns_same(self) -> None:
        tags = ["tree", "sky", "mountain"]
        assert apply_overrides(tags, {}) == tags

    def test_applies_matching_overrides(self) -> None:
        tags = ["tree", "sky", "mountain"]
        overrides = {"tree": "baum", "sky": "himmel"}
        result = apply_overrides(tags, overrides)
        assert result == ["baum", "himmel", "mountain"]

    def test_unmatched_tags_pass_through(self) -> None:
        tags = ["cat", "dog"]
        overrides = {"bird": "vogel"}
        assert apply_overrides(tags, overrides) == ["cat", "dog"]


# ---------------------------------------------------------------------------
# collect_images
# ---------------------------------------------------------------------------

class TestCollectImages:
    def test_collects_single_file(self, sample_image: Path) -> None:
        result = collect_images((str(sample_image),))
        assert len(result) == 1
        assert result[0] == sample_image

    def test_skips_non_image_files(self, non_image_file: Path) -> None:
        result = collect_images((str(non_image_file),))
        assert len(result) == 0

    def test_collects_from_directory(self, sample_images: list[Path]) -> None:
        directory = sample_images[0].parent
        result = collect_images((str(directory),))
        assert len(result) == len(sample_images)

    def test_recursive_scan(self, tmp_path: Path, sample_image: Path) -> None:
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        import shutil
        dest = subdir / "nested.png"
        shutil.copy(sample_image, dest)

        # Non-recursive should find only the root image
        result_flat = collect_images((str(tmp_path),), recursive=False)
        assert all(r.parent == tmp_path for r in result_flat)

        # Recursive should find nested image too
        result_recursive = collect_images((str(tmp_path),), recursive=True)
        assert any(r.parent == subdir for r in result_recursive)

    def test_empty_directory(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        result = collect_images((str(empty),))
        assert len(result) == 0

    def test_nonexistent_path(self) -> None:
        result = collect_images(("/nonexistent/path",))
        assert len(result) == 0


# ---------------------------------------------------------------------------
# format_tags_text
# ---------------------------------------------------------------------------

class TestFormatTagsText:
    def test_pipe_separated(self) -> None:
        result = format_tags_text(["tree", "sky", "mountain"])
        assert result == "tree | sky | mountain"

    def test_with_confidence(self) -> None:
        result = format_tags_text(
            ["tree", "sky"],
            confidences=[0.95, 0.80],
            show_confidence=True,
        )
        assert "95" in result
        assert "80" in result
        assert "tree" in result
        assert "sky" in result

    def test_empty_tags(self) -> None:
        result = format_tags_text([])
        assert result == ""

    def test_confidence_flag_without_values(self) -> None:
        result = format_tags_text(["tree"], show_confidence=True)
        assert result == "tree"
