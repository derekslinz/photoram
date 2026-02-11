"""CLI integration smoke tests for photoram.

These tests verify the CLI contract without loading the actual model.
They use Click's CliRunner for isolated invocations.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from photoram.cli import main
from photoram.errors import EXIT_INVALID_ARGS, EXIT_NO_IMAGES, EXIT_SUCCESS
from photoram.schemas import BatchResult, TagResult


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _mock_batch(*tags_lists: list[str]) -> BatchResult:
    """Build a BatchResult from tag lists for mocking."""
    results = []
    for i, tags in enumerate(tags_lists):
        results.append(TagResult(
            path=f"image_{i}.jpg",
            tags=tags,
            confidences=[0.9 - j * 0.1 for j in range(len(tags))],
        ))
    return BatchResult(results=results)


# ---------------------------------------------------------------------------
# Version / help
# ---------------------------------------------------------------------------

class TestCLIBasics:
    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "photoram-cli" in result.output

    def test_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "tag" in result.output
        assert "info" in result.output

    def test_short_help_alias(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["-h"])
        assert result.exit_code == 0
        assert "tag" in result.output
        assert "info" in result.output

    def test_tag_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["tag", "--help"])
        assert result.exit_code == 0
        assert "--threshold" in result.output
        assert "--batch-size" in result.output
        assert "--timings" in result.output
        assert "--device" not in result.output

    def test_tag_short_help_alias(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["tag", "-h"])
        assert result.exit_code == 0
        assert "--threshold" in result.output
        assert "--timings" in result.output
        assert "--device" not in result.output

    def test_info_help_hides_device(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["info", "--help"])
        assert result.exit_code == 0
        assert "--device" not in result.output


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_threshold_below_range(self, runner: CliRunner, sample_image: Path) -> None:
        result = runner.invoke(main, ["tag", str(sample_image), "-t", "-0.1"])
        assert result.exit_code != 0

    def test_threshold_above_range(self, runner: CliRunner, sample_image: Path) -> None:
        result = runner.invoke(main, ["tag", str(sample_image), "-t", "1.5"])
        assert result.exit_code != 0

    def test_top_n_zero(self, runner: CliRunner, sample_image: Path) -> None:
        result = runner.invoke(main, ["tag", str(sample_image), "-n", "0"])
        assert result.exit_code != 0

    def test_top_n_negative(self, runner: CliRunner, sample_image: Path) -> None:
        result = runner.invoke(main, ["tag", str(sample_image), "-n", "-1"])
        assert result.exit_code != 0

    def test_batch_size_zero(self, runner: CliRunner, sample_image: Path) -> None:
        result = runner.invoke(main, ["tag", str(sample_image), "--batch-size", "0"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# JSON output contract: always a list
# ---------------------------------------------------------------------------

class TestJSONContract:
    @patch("photoram.cli.TaggingService")
    def test_single_image_returns_list(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.1
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _mock_batch(["tree", "sky"])

        result = runner.invoke(main, [
            "tag", str(sample_image), "-f", "json", "-q",
        ])
        assert result.exit_code == EXIT_SUCCESS
        data = json.loads(result.output)
        assert isinstance(data, list), "JSON output must always be a list"
        assert len(data) == 1

    @patch("photoram.cli.TaggingService")
    def test_multiple_images_returns_list(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_images: list[Path]
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.1
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _mock_batch(
            ["tree"], ["sky"], ["mountain"], ["lake"]
        )

        result = runner.invoke(main, [
            "tag", *[str(p) for p in sample_images], "-f", "json", "-q",
        ])
        assert result.exit_code == EXIT_SUCCESS
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 4


# ---------------------------------------------------------------------------
# Text output
# ---------------------------------------------------------------------------

class TestTextOutput:
    @patch("photoram.cli.TaggingService")
    def test_single_image_text(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.1
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _mock_batch(["tree", "sky"])

        result = runner.invoke(main, [
            "tag", str(sample_image), "-q",
        ])
        assert result.exit_code == EXIT_SUCCESS
        assert "tree" in result.output
        assert "sky" in result.output


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

class TestCSVOutput:
    @patch("photoram.cli.TaggingService")
    def test_csv_has_header(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.1
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _mock_batch(["tree"])

        result = runner.invoke(main, [
            "tag", str(sample_image), "-f", "csv", "-q",
        ])
        assert result.exit_code == EXIT_SUCCESS
        lines = result.output.strip().split("\n")
        assert "file" in lines[0]
        assert "tags" in lines[0]


# ---------------------------------------------------------------------------
# No images found
# ---------------------------------------------------------------------------

class TestNoImages:
    @patch("photoram.cli.TaggingService")
    def test_no_images_exit_code(
        self, mock_svc_cls: MagicMock, runner: CliRunner, non_image_file: Path
    ) -> None:
        from photoram.errors import NoImagesError

        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.1
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.side_effect = NoImagesError("No images found")

        result = runner.invoke(main, [
            "tag", str(non_image_file), "-q",
        ])
        assert result.exit_code == EXIT_NO_IMAGES
