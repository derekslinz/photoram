"""Tests for photoram.errors — exit codes and exceptions."""

from __future__ import annotations

from photoram.errors import (
    EXIT_INVALID_ARGS,
    EXIT_MODEL_ERROR,
    EXIT_NO_IMAGES,
    EXIT_SUCCESS,
    CheckpointDownloadError,
    ModelError,
    NoImagesError,
    PhotoramError,
    ValidationError,
)


class TestExitCodes:
    def test_success_is_zero(self) -> None:
        assert EXIT_SUCCESS == 0

    def test_codes_are_distinct(self) -> None:
        codes = {EXIT_SUCCESS, EXIT_NO_IMAGES, EXIT_INVALID_ARGS, EXIT_MODEL_ERROR}
        assert len(codes) == 4


class TestExceptions:
    def test_validation_error_exit_code(self) -> None:
        e = ValidationError("bad threshold")
        assert e.exit_code == EXIT_INVALID_ARGS

    def test_no_images_error_exit_code(self) -> None:
        e = NoImagesError("nothing found")
        assert e.exit_code == EXIT_NO_IMAGES

    def test_model_error_exit_code(self) -> None:
        e = ModelError("failed to load")
        assert e.exit_code == EXIT_MODEL_ERROR

    def test_checkpoint_download_inherits_model_error(self) -> None:
        e = CheckpointDownloadError("network fail")
        assert isinstance(e, ModelError)
        assert isinstance(e, PhotoramError)

    def test_custom_exit_code_override(self) -> None:
        e = PhotoramError("custom", exit_code=42)
        assert e.exit_code == 42
