"""TaggingService — orchestration layer between CLI and model backend.

This module decouples the CLI from inference internals. The CLI delegates
all tagging orchestration to TaggingService, which owns:
  • Model lifecycle (load, warm-up)
  • Image collection and validation
  • Tag overrides and post-processing (top-n, override map)
  • Batch/single dispatch
  • Result aggregation into BatchResult
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Optional, Sequence

from .errors import NoImagesError, ValidationError
from .model import RAMPlusModel
from .schemas import BatchResult, TagResult
from .utils import apply_overrides, collect_images, load_overrides


class TaggingService:
    """High-level tagging orchestrator.

    Usage::

        svc = TaggingService(threshold=0.5, device="mps")
        svc.load_model()
        batch = svc.tag_paths(["photo.jpg", "./album/"], recursive=True)
        for r in batch.results:
            print(r.tags)
    """

    def __init__(
        self,
        threshold: float = 0.68,
        device: Optional[str] = None,
        image_size: int = 384,
        top_n: Optional[int] = None,
        overrides: Optional[str] = None,
        batch_size: int = 1,
    ) -> None:
        # --- Validate inputs early ---
        self._validate_threshold(threshold)
        self._validate_top_n(top_n)
        self._validate_batch_size(batch_size)

        self.threshold = threshold
        self.device = device
        self.image_size = image_size
        self.top_n = top_n
        self.batch_size = batch_size

        self.override_map = load_overrides(overrides)

        self._model: Optional[RAMPlusModel] = None
        self._load_time: float = 0.0

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_threshold(value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValidationError(
                f"Threshold must be between 0.0 and 1.0, got {value}."
            )

    @staticmethod
    def _validate_top_n(value: Optional[int]) -> None:
        if value is not None and value < 1:
            raise ValidationError(
                f"--top-n must be a positive integer, got {value}."
            )

    @staticmethod
    def _validate_batch_size(value: int) -> None:
        if value < 1:
            raise ValidationError(
                f"--batch-size must be a positive integer, got {value}."
            )

    # ------------------------------------------------------------------
    # Model lifecycle
    # ------------------------------------------------------------------

    def load_model(self) -> float:
        """Load (or warm up) the RAM++ model.

        Returns:
            Wall-clock seconds the model load took.

        Raises:
            ModelError: on any model/checkpoint failure.
        """
        t0 = time.time()
        self._model = RAMPlusModel(
            device=self.device,
            image_size=self.image_size,
            threshold=self.threshold,
        )
        # Force the lazy model property to materialise
        _ = self._model.model
        self._load_time = time.time() - t0
        return self._load_time

    @property
    def model(self) -> RAMPlusModel:
        if self._model is None:
            self.load_model()
        return self._model

    @property
    def resolved_device(self) -> str:
        """Return the device string after model is loaded."""
        return str(self.model.device)

    @property
    def load_time(self) -> float:
        return self._load_time

    # ------------------------------------------------------------------
    # High-level tagging
    # ------------------------------------------------------------------

    def tag_paths(
        self,
        input_paths: Sequence[str],
        recursive: bool = False,
        on_progress: Optional[Callable[[Path, int, int], None]] = None,
    ) -> BatchResult:
        """Collect images from *input_paths* and tag them.

        Args:
            input_paths: File or directory paths.
            recursive:   Recurse into subdirectories.
            on_progress: Optional callback(image_path, current, total).

        Returns:
            BatchResult containing one TagResult per image.

        Raises:
            NoImagesError: if no valid images are found.
        """
        images = collect_images(tuple(input_paths), recursive=recursive)
        if not images:
            raise NoImagesError(
                "No supported images found in the provided paths.\n"
                "Supported formats: JPEG, PNG, TIFF, BMP, WebP, HEIC, GIF."
            )

        return self.tag_files(images, on_progress=on_progress)

    def tag_files(
        self,
        image_paths: Sequence[Path],
        on_progress: Optional[Callable[[Path, int, int], None]] = None,
    ) -> BatchResult:
        """Tag a pre-resolved list of image paths.

        Uses batch inference when batch_size > 1.
        """
        mdl = self.model
        total = len(image_paths)
        results: list[TagResult] = []

        if self.batch_size > 1:
            # Batch inference path
            raw_results = mdl.tag_images(list(image_paths), batch_size=self.batch_size)
            for idx, result in enumerate(raw_results):
                self._post_process(result)
                results.append(result)
                if on_progress:
                    on_progress(Path(result.path), idx + 1, total)
        else:
            # Sequential path (default)
            for idx, img_path in enumerate(image_paths):
                if on_progress:
                    on_progress(img_path, idx, total)

                result = mdl.tag_image(img_path)
                self._post_process(result)
                results.append(result)

                if on_progress:
                    on_progress(img_path, idx + 1, total)

        return BatchResult(results=results)

    # ------------------------------------------------------------------
    # Post-processing
    # ------------------------------------------------------------------

    def _post_process(self, result: TagResult) -> None:
        """Apply overrides and top-n truncation in place."""
        if not result.success:
            return

        # Tag overrides
        result.tags = apply_overrides(result.tags, self.override_map)

        # Top-N limit
        if self.top_n:
            result.tags = result.tags[: self.top_n]
            result.confidences = result.confidences[: self.top_n]
