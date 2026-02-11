"""Standardized exit codes and custom exceptions for photoram."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Exit codes
# ---------------------------------------------------------------------------

EXIT_SUCCESS = 0
EXIT_NO_IMAGES = 1
EXIT_INVALID_ARGS = 2
EXIT_MODEL_ERROR = 3
EXIT_RUNTIME_ERROR = 4


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class PhotoramError(Exception):
    """Base exception for photoram."""

    exit_code: int = EXIT_RUNTIME_ERROR

    def __init__(self, message: str, exit_code: int | None = None) -> None:
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class ValidationError(PhotoramError):
    """Invalid user input (threshold, top-n, device, etc.)."""

    exit_code = EXIT_INVALID_ARGS


class NoImagesError(PhotoramError):
    """No valid images found for the provided input paths."""

    exit_code = EXIT_NO_IMAGES


class ModelError(PhotoramError):
    """Model loading, download, or inference failure."""

    exit_code = EXIT_MODEL_ERROR


class CheckpointDownloadError(ModelError):
    """Failed to download the model checkpoint."""


class CheckpointCorruptionError(ModelError):
    """Downloaded checkpoint appears corrupted."""


class CheckpointIntegrityError(ModelError):
    """Downloaded checkpoint failed integrity verification."""


class MetadataWriteError(PhotoramError):
    """Failed to write metadata to one or more images."""
