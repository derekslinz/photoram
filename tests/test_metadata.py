"""Tests for metadata writing safeguards."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from photoram.metadata import write_metadata_exiftool


@patch("photoram.metadata._has_exiftool", return_value=True)
@patch("photoram.metadata.subprocess.run")
def test_exiftool_uses_double_dash_before_filename(
    mock_run: MagicMock,
    _mock_has_exiftool: MagicMock,
    tmp_path: Path,
) -> None:
    target = tmp_path / "-starts-with-dash.jpg"
    target.write_text("x", encoding="utf-8")

    mock_run.return_value = MagicMock(returncode=0, stderr="")

    write_metadata_exiftool(target, ["tree", "sky"])

    args = mock_run.call_args.args[0]
    assert "--" in args
    assert args[-2] == "--"
    assert args[-1] == str(target)
