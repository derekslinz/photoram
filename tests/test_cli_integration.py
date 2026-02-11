"""Additional CLI integration tests for command contracts."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from photoram.cli import main
from photoram.errors import EXIT_SUCCESS, MetadataWriteError
from photoram.schemas import BatchResult, TagResult


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _single_success_batch(
    path: str = "image.jpg",
    tags: list[str] | None = None,
    confidences: list[float] | None = None,
) -> BatchResult:
    if tags is None:
        tags = ["tree", "sky"]
    if confidences is None:
        confidences = [0.91, 0.82]
    return BatchResult(
        results=[
            TagResult(
                path=path,
                tags=tags,
                confidences=confidences,
            )
        ]
    )


class TestCLIOutputIntegration:
    @patch("photoram.cli.TaggingService")
    def test_output_flag_writes_file(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path, tmp_path: Path
    ) -> None:
        output_file = tmp_path / "result.txt"

        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.01
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _single_success_batch()

        result = runner.invoke(
            main,
            ["tag", str(sample_image), "--output", str(output_file), "--quiet"],
        )
        assert result.exit_code == EXIT_SUCCESS
        assert result.output.strip() == ""
        assert output_file.exists()
        assert "tree" in output_file.read_text(encoding="utf-8")

    @patch("photoram.cli.TaggingService")
    def test_json_confidence_flag_controls_field(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.01
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _single_success_batch(confidences=[0.9, 0.8])

        result_without = runner.invoke(
            main,
            ["tag", str(sample_image), "--format", "json", "--quiet"],
        )
        assert result_without.exit_code == EXIT_SUCCESS
        data_without = json.loads(result_without.output)
        assert "confidences" not in data_without[0]

        result_with = runner.invoke(
            main,
            ["tag", str(sample_image), "--format", "json", "--confidence", "--quiet"],
        )
        assert result_with.exit_code == EXIT_SUCCESS
        data_with = json.loads(result_with.output)
        assert data_with[0]["confidences"] == [0.9, 0.8]

    @patch("photoram.cli.TaggingService")
    def test_photils_compat_image_alias(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.01
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _single_success_batch(path=str(sample_image))

        result = runner.invoke(main, ["tag", "--image", str(sample_image), "--quiet"])

        assert result.exit_code == EXIT_SUCCESS
        called_args, called_kwargs = mock_svc.tag_paths.call_args
        assert called_args[0] == (str(sample_image),)
        assert called_kwargs["recursive"] is False

    @patch("photoram.cli.TaggingService")
    def test_photils_compat_output_and_confidence_aliases(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path, tmp_path: Path
    ) -> None:
        output_file = tmp_path / "compat_output.txt"

        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.01
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _single_success_batch(confidences=[0.95, 0.9])

        result = runner.invoke(
            main,
            [
                "tag",
                str(sample_image),
                "--output_file",
                str(output_file),
                "--with_confidence",
                "--quiet",
            ],
        )

        assert result.exit_code == EXIT_SUCCESS
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "tree" in content
        assert "0.95" in content

    def test_tag_requires_input_when_no_compat_image(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["tag"])
        assert result.exit_code == 2
        # With mix_stderr=True, stderr is mixed into output
        assert "Missing argument 'INPUT...'" in result.output

    @patch("photoram.cli.TaggingService")
    def test_timings_flag_prints_basic_timings(
        self, mock_svc_cls: MagicMock, runner: CliRunner, sample_image: Path
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.01
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = _single_success_batch()

        result = runner.invoke(main, ["tag", str(sample_image), "-T", "--quiet"])

        assert result.exit_code == EXIT_SUCCESS
        assert "Timings:" in result.output
        assert "model load:" in result.output
        assert "tagging:" in result.output
        assert "total:" in result.output


class TestCLIMetadataIntegration:
    @patch("photoram.cli.write_metadata")
    @patch("photoram.cli.TaggingService")
    def test_metadata_write_errors_do_not_fail_command(
        self,
        mock_svc_cls: MagicMock,
        mock_write_metadata: MagicMock,
        runner: CliRunner,
        sample_image: Path,
    ) -> None:
        mock_svc = MagicMock()
        mock_svc_cls.return_value = mock_svc
        mock_svc.load_model.return_value = 0.01
        mock_svc.resolved_device = "cpu"
        mock_svc.tag_paths.return_value = BatchResult(
            results=[
                TagResult(path=str(sample_image), tags=["tree"]),
                TagResult(path="failed.jpg", tags=[], error="decode failed"),
            ]
        )
        mock_write_metadata.side_effect = MetadataWriteError("mock metadata failure")

        result = runner.invoke(
            main,
            ["tag", str(sample_image), "--write-metadata", "--quiet"],
        )

        assert result.exit_code == EXIT_SUCCESS
        mock_write_metadata.assert_called_once_with(str(sample_image), ["tree"])
