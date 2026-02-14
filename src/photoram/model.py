"""Model loading, caching, and inference for ImageNet-21K classification."""

from __future__ import annotations

import os
import re
import warnings
from pathlib import Path
from typing import Any, Optional

from PIL import Image

from .errors import ModelError
from .schemas import TagResult

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HF_MODEL_ID = os.environ.get("PHOTORAM_IMAGENET21K_MODEL", "vit_base_patch16_224.augreg_in21k")
HF_CACHE_DIR = Path(os.environ.get(
    "HF_HOME",
    Path.home() / ".cache" / "huggingface",
))

DEFAULT_IMAGE_SIZE = 224
DEFAULT_THRESHOLD = 0.0
DEFAULT_TOP_K = 256

DEFAULT_MAX_IMAGE_PIXELS = 120_000_000
MAX_IMAGE_PIXELS = max(
    1,
    int(os.environ.get("PHOTORAM_MAX_IMAGE_PIXELS", DEFAULT_MAX_IMAGE_PIXELS)),
)

# Keep PIL decompression-bomb protection enabled with an explicit project bound.
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


# ---------------------------------------------------------------------------
# Model manager
# ---------------------------------------------------------------------------

class ImageNet21KModel:
    """Wrapper around a TIMM ImageNet-21K classification model."""

    def __init__(
        self,
        device: Optional[str] = None,
        image_size: int = DEFAULT_IMAGE_SIZE,
        threshold: float = DEFAULT_THRESHOLD,
        top_k: int = DEFAULT_TOP_K,
        model_id: str = HF_MODEL_ID,
    ) -> None:
        self.image_size = image_size
        self.threshold = threshold
        self.top_k = max(1, top_k)
        self.model_id = model_id

        self.device = self._resolve_device(device)

        self._transform: Optional[Any] = None
        self._model: Optional[Any] = None
        self._id2label: dict[int, str] = {}

    # ------------------------------------------------------------------
    # Device resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_device(device: Optional[str] = None) -> "torch.device":
        import torch

        if device:
            try:
                return torch.device(device)
            except RuntimeError as e:
                raise ModelError(
                    f"Invalid device '{device}'. Valid options: cpu, cuda, mps.\n"
                    f"  Detail: {e}"
                ) from e
        if torch.cuda.is_available():
            return torch.device("cuda")
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    # ------------------------------------------------------------------
    # Lazy model loading
    # ------------------------------------------------------------------

    @property
    def model(self) -> Any:
        if self._model is None:
            try:
                import timm
                from timm.data import create_transform, resolve_model_data_config

                self._model = timm.create_model(self.model_id, pretrained=True)
                self._model.eval()
                self._model = self._model.to(self.device)

                data_cfg = resolve_model_data_config(self._model)
                self._transform = create_transform(**data_cfg, is_training=False)
                self._id2label = self._extract_id2label(self._model)
            except Exception as e:
                raise ModelError(
                    f"Failed to load ImageNet-21K model ({self.model_id}): {e}\n\n"
                    "Remediation:\n"
                    "  • Ensure internet access on first run\n"
                    f"  • Clear model cache if corrupted: rm -rf {HF_CACHE_DIR}\n"
                    "  • Force CPU for low-memory hosts: --device cpu"
                ) from e
        return self._model

    @property
    def transform(self) -> Any:
        if self._transform is None:
            _ = self.model
        return self._transform

    @staticmethod
    def _normalize_label(label: str) -> str:
        cleaned = label.strip().replace("_", " ")
        if "," in cleaned:
            cleaned = cleaned.split(",", 1)[0].strip()
        return cleaned

    @staticmethod
    def _is_placeholder_label(label: str) -> bool:
        return bool(re.fullmatch(r"label[\s_\-]*\d+", label.strip().lower()))

    @staticmethod
    def _extract_id2label(model: Any) -> dict[int, str]:
        # Preferred path: use TIMM ImageNet metadata that includes 21K labels.
        try:
            from timm.data.imagenet_info import ImageNetInfo, infer_imagenet_subset

            subset = infer_imagenet_subset(model)
            if subset:
                info = ImageNetInfo(subset=subset)
                num_classes = int(getattr(model, "num_classes", 0) or info.num_classes())
                labels: dict[int, str] = {}
                shared = min(num_classes, info.num_classes())

                for idx in range(shared):
                    desc = str(info.index_to_description(idx))
                    normalized = ImageNet21KModel._normalize_label(desc)
                    labels[idx] = normalized if normalized else f"class_{idx}"

                for idx in range(shared, num_classes):
                    labels[idx] = f"class_{idx}"

                if labels:
                    return labels
        except Exception:
            pass

        # Fallback path for non-TIMM models.
        raw = getattr(getattr(model, "config", object()), "id2label", None) or {}

        id2label: dict[int, str] = {}
        placeholder_count = 0
        for key, value in raw.items():
            try:
                idx = int(key)
            except (TypeError, ValueError):
                continue

            normalized = ImageNet21KModel._normalize_label(str(value))
            if not normalized:
                normalized = f"class_{idx}"
            if ImageNet21KModel._is_placeholder_label(normalized):
                placeholder_count += 1
                normalized = f"class_{idx}"
            id2label[idx] = normalized

        if id2label and placeholder_count < len(id2label):
            return id2label

        num_classes = int(
            getattr(model, "num_classes", 0)
            or getattr(getattr(model, "config", object()), "num_labels", 0)
            or len(id2label)
            or 0
        )
        return {i: id2label.get(i, f"class_{i}") for i in range(max(0, num_classes))}

    # ------------------------------------------------------------------
    # Image decoding helpers
    # ------------------------------------------------------------------

    def _load_image_tensor(
        self,
        image_path: str | Path,
    ) -> tuple["Image.Image | None", float | None, str | None]:
        """Decode one image with safety checks.

        Returns:
            (rgb_image, megapixels, error_message)
        """
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            try:
                with Image.open(image_path) as pil_image:
                    width, height = pil_image.size
                    total_pixels = width * height
                    if total_pixels > MAX_IMAGE_PIXELS:
                        raise Image.DecompressionBombError(
                            f"Image has {total_pixels:,} pixels; maximum allowed is {MAX_IMAGE_PIXELS:,}."
                        )

                    image_mp = total_pixels / 1_000_000
                    rgb_image = pil_image.convert("RGB")
                    return rgb_image, image_mp, None
            except (Image.DecompressionBombError, Image.DecompressionBombWarning) as e:
                return None, None, f"Image rejected for safety: {e}"
            except Exception as e:
                return None, None, f"Failed to load image: {e}"

    # ------------------------------------------------------------------
    # Single-image inference
    # ------------------------------------------------------------------

    def tag_image(self, image_path: str | Path) -> TagResult:
        """Run ImageNet-21K classification on a single image."""
        image, image_mp, error = self._load_image_tensor(image_path)
        if error is not None or image is None or image_mp is None:
            return TagResult(
                path=str(image_path),
                tags=[],
                confidences=[],
                error=error or "Failed to load image.",
            )

        tags_en, confidences = self._batch_inference_with_confidence([image])[0]

        return TagResult(
            path=str(image_path),
            tags=tags_en,
            confidences=confidences,
            image_megapixels=image_mp,
        )

    # ------------------------------------------------------------------
    # Batch inference
    # ------------------------------------------------------------------

    def tag_images(
        self,
        image_paths: list[str | Path],
        batch_size: int = 4,
    ) -> list[TagResult]:
        """Run ImageNet-21K classification on multiple images."""
        indexed_results: list[tuple[int, TagResult]] = []
        pending_indices: list[int] = []
        pending_images: list[Image.Image] = []
        pending_megapixels: list[float] = []

        def _flush_batch() -> None:
            if not pending_images:
                return

            batch_tags = self._batch_inference_with_confidence(pending_images)

            for pos, (tags_en, confs) in enumerate(batch_tags):
                src_idx = pending_indices[pos]
                indexed_results.append((
                    src_idx,
                    TagResult(
                        path=str(image_paths[src_idx]),
                        tags=tags_en,
                        confidences=confs,
                        image_megapixels=pending_megapixels[pos],
                    ),
                ))

            pending_indices.clear()
            pending_images.clear()
            pending_megapixels.clear()

        for idx, img_path in enumerate(image_paths):
            image, image_mp, error = self._load_image_tensor(img_path)
            if error is not None or image is None or image_mp is None:
                indexed_results.append((
                    idx,
                    TagResult(
                        path=str(img_path),
                        tags=[],
                        confidences=[],
                        error=error or "Failed to load image.",
                    ),
                ))
                continue

            pending_indices.append(idx)
            pending_images.append(image)
            pending_megapixels.append(image_mp)

            if len(pending_images) >= batch_size:
                _flush_batch()

        _flush_batch()

        indexed_results.sort(key=lambda x: x[0])
        return [result for _, result in indexed_results]

    # ------------------------------------------------------------------
    # Core inference
    # ------------------------------------------------------------------

    def _batch_inference_with_confidence(
        self,
        images: list["Image.Image"],
    ) -> list[tuple[list[str], list[float]]]:
        """Batch inference returning top labels and probabilities for each image."""
        import torch

        model = self.model
        transform = self.transform

        pixel_values = [transform(image) for image in images]
        inputs = torch.stack(pixel_values).to(self.device)

        with torch.no_grad():
            outputs = model(inputs)
            logits = outputs.logits if hasattr(outputs, "logits") else outputs
            probs = torch.softmax(logits, dim=-1)

        num_classes = int(probs.shape[-1])
        k = min(self.top_k, num_classes)
        top_probs, top_indices = torch.topk(probs, k=k, dim=-1)

        results: list[tuple[list[str], list[float]]] = []

        for row_probs, row_indices in zip(top_probs.tolist(), top_indices.tolist()):
            tags: list[str] = []
            confs: list[float] = []

            for confidence, index in zip(row_probs, row_indices):
                score = float(confidence)
                if score < self.threshold:
                    continue

                label = self._id2label.get(int(index), f"class_{int(index)}")
                tags.append(label)
                confs.append(round(score, 4))

            results.append((tags, confs))

        return results


# Backwards-compatible alias for code importing the old class name.
RAMPlusModel = ImageNet21KModel
