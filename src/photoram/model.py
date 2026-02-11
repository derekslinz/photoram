"""Model loading, caching, and inference for RAM++."""

from __future__ import annotations

import contextlib
import hashlib
import os
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from .errors import (
    CheckpointCorruptionError,
    CheckpointDownloadError,
    CheckpointIntegrityError,
    ModelError,
)
from .schemas import TagResult

# Suppress timm deprecation warnings from the RAM package
warnings.filterwarnings("ignore", category=FutureWarning, module="timm")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HF_REPO_ID = "xinyu1205/recognize-anything-plus-model"
HF_FILENAME = "ram_plus_swin_large_14m.pth"
HF_CHECKPOINT_SHA256 = "497c178836ba66698ca226c7895317e6e800034be986452dbd2593298d50e87d"

DEFAULT_IMAGE_SIZE = 384
DEFAULT_THRESHOLD = 0.68
SUPPORTED_IMAGE_SIZES = {224, 384}

DEFAULT_MAX_IMAGE_PIXELS = 120_000_000
MAX_IMAGE_PIXELS = max(
    1,
    int(os.environ.get("PHOTORAM_MAX_IMAGE_PIXELS", DEFAULT_MAX_IMAGE_PIXELS)),
)

# Minimum reasonable checkpoint size (100 MB) — guards against truncated downloads
_MIN_CHECKPOINT_BYTES = 100 * 1024 * 1024
_HASH_CHUNK_SIZE = 1024 * 1024

CACHE_DIR = Path(os.environ.get(
    "PHOTORAM_CACHE",
    Path.home() / ".cache" / "photoram",
))

# Keep PIL decompression-bomb protection enabled with an explicit project bound.
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


# ---------------------------------------------------------------------------
# Model manager
# ---------------------------------------------------------------------------

class RAMPlusModel:
    """Wrapper around the RAM++ model with auto-download and device handling."""

    def __init__(
        self,
        device: Optional[str] = None,
        image_size: int = DEFAULT_IMAGE_SIZE,
        threshold: float = DEFAULT_THRESHOLD,
        pretrained_path: Optional[str] = None,
    ) -> None:
        self.image_size = self._resolve_ram_image_size(image_size)
        self.threshold = threshold

        try:
            self.pretrained_path = pretrained_path or str(self._ensure_checkpoint())
        except (CheckpointDownloadError, CheckpointCorruptionError, CheckpointIntegrityError):
            raise
        except Exception as e:
            raise CheckpointDownloadError(
                f"Unexpected error obtaining model checkpoint: {e}\n"
                f"Try deleting the cache directory and retrying:\n"
                f"  rm -rf {CACHE_DIR}"
            ) from e

        # Lazy-import heavy deps
        import torch
        from ram import get_transform

        self.device = self._resolve_device(device)
        self.transform = get_transform(image_size=self.image_size)

        self._model: Optional[torch.nn.Module] = None

    @staticmethod
    def _resolve_ram_image_size(image_size: int) -> int:
        """Normalize unsupported image sizes to a known-good RAM++ setting.

        RAM++ (swin_b/swin_l paths) only supports 224 and 384 in upstream code.
        Other values can raise:
          UnboundLocalError: local variable 'vision_config_path' referenced before assignment
        """
        if image_size in SUPPORTED_IMAGE_SIZES:
            return image_size

        warnings.warn(
            "RAM++ only supports image sizes 224 or 384 for Swin backbones. "
            f"Received {image_size}; falling back to {DEFAULT_IMAGE_SIZE} "
            "to avoid upstream vision_config_path errors.",
            RuntimeWarning,
            stacklevel=2,
        )
        return DEFAULT_IMAGE_SIZE

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
    # Checkpoint download & validation
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_cache_dir_permissions() -> None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # Best-effort: enforce private cache directory on POSIX systems.
        with contextlib.suppress(OSError):
            os.chmod(CACHE_DIR, 0o700)

    @staticmethod
    def _sha256_file(path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(_HASH_CHUNK_SIZE), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def _validate_checkpoint(path: Path) -> None:
        size = path.stat().st_size
        if size < _MIN_CHECKPOINT_BYTES:
            raise CheckpointCorruptionError(
                f"Checkpoint appears corrupted ({size:,} bytes).\n"
                f"Delete and retry:\n"
                f"  rm {path}\n"
                f"  photoram-cli info"
            )

        actual_sha256 = RAMPlusModel._sha256_file(path)
        if actual_sha256 != HF_CHECKPOINT_SHA256:
            raise CheckpointIntegrityError(
                "Checkpoint integrity verification failed.\n"
                f"  expected sha256: {HF_CHECKPOINT_SHA256}\n"
                f"  actual sha256:   {actual_sha256}\n"
                f"Delete the checkpoint and retry:\n"
                f"  rm {path}\n"
                f"  photoram-cli info"
            )

    @staticmethod
    def _ensure_checkpoint() -> Path:
        """Download the RAM++ checkpoint from HuggingFace if not cached."""
        dest = CACHE_DIR / HF_FILENAME

        if dest.exists():
            RAMPlusModel._validate_checkpoint(dest)
            return dest

        RAMPlusModel._ensure_cache_dir_permissions()

        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            raise CheckpointDownloadError(
                "huggingface-hub is not installed. Reinstall photoram:\n"
                "  pip install -e ."
            )

        try:
            downloaded = hf_hub_download(
                repo_id=HF_REPO_ID,
                filename=HF_FILENAME,
                local_dir=str(CACHE_DIR),
                local_dir_use_symlinks=False,
            )
        except OSError as e:
            raise CheckpointDownloadError(
                f"Network error downloading model checkpoint:\n  {e}\n\n"
                f"Remediation:\n"
                f"  • Check your internet connection\n"
                f"  • If behind a proxy, set HTTPS_PROXY\n"
                f"  • Try again: photoram-cli info"
            ) from e
        except Exception as e:
            raise CheckpointDownloadError(
                f"Failed to download model checkpoint:\n  {e}\n\n"
                f"Remediation:\n"
                f"  • Ensure you have write access to {CACHE_DIR}\n"
                f"  • Try again: photoram-cli info"
            ) from e

        path = Path(downloaded)

        try:
            RAMPlusModel._validate_checkpoint(path)
        except (CheckpointCorruptionError, CheckpointIntegrityError):
            with contextlib.suppress(OSError):
                path.unlink(missing_ok=True)
            raise

        return path

    # ------------------------------------------------------------------
    # Lazy model loading
    # ------------------------------------------------------------------

    @property
    def model(self) -> "torch.nn.Module":
        if self._model is None:
            try:
                from ram.models import ram_plus

                self._model = ram_plus(
                    pretrained=self.pretrained_path,
                    image_size=self.image_size,
                    vit="swin_l",
                )
                self._model.eval()
                self._model = self._model.to(self.device)
            except Exception as e:
                raise ModelError(
                    f"Failed to load RAM++ model: {e}\n\n"
                    f"Remediation:\n"
                    f"  • Ensure checkpoint is not corrupted: rm -rf {CACHE_DIR}\n"
                    f"  • Ensure sufficient GPU memory or use --device cpu"
                ) from e
        return self._model

    # ------------------------------------------------------------------
    # Image decoding helpers
    # ------------------------------------------------------------------

    def _load_image_tensor(
        self,
        image_path: str | Path,
    ) -> tuple["torch.Tensor | None", float | None, str | None]:
        """Decode and transform one image with safety checks.

        Returns:
            (tensor, megapixels, error_message)
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
                    tensor = self.transform(pil_image).to(self.device)
                    return tensor, image_mp, None
            except (Image.DecompressionBombError, Image.DecompressionBombWarning) as e:
                return None, None, f"Image rejected for safety: {e}"
            except Exception as e:
                return None, None, f"Failed to load image: {e}"

    # ------------------------------------------------------------------
    # Single-image inference
    # ------------------------------------------------------------------

    def tag_image(self, image_path: str | Path) -> TagResult:
        """Run RAM++ on a single image and return tags with confidences."""
        import torch

        image, image_mp, error = self._load_image_tensor(image_path)
        if error is not None or image is None or image_mp is None:
            return TagResult(
                path=str(image_path),
                tags=[],
                confidences=[],
                error=error or "Failed to load image.",
            )

        with torch.no_grad():
            tags_en, confidences = self._inference_with_confidence(image.unsqueeze(0))

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
        """Run RAM++ on multiple images with optional batching.

        This implementation streams image decoding in mini-batches to keep
        memory usage bounded by ``batch_size``.
        """
        import torch

        indexed_results: list[tuple[int, TagResult]] = []
        pending_indices: list[int] = []
        pending_tensors: list["torch.Tensor"] = []
        pending_megapixels: list[float] = []

        def _flush_batch() -> None:
            if not pending_tensors:
                return

            tensors = torch.stack(pending_tensors).to(self.device)
            with torch.no_grad():
                batch_tags = self._batch_inference_with_confidence(tensors)

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
            pending_tensors.clear()
            pending_megapixels.clear()

        for idx, img_path in enumerate(image_paths):
            tensor, image_mp, error = self._load_image_tensor(img_path)
            if error is not None or tensor is None or image_mp is None:
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
            pending_tensors.append(tensor)
            pending_megapixels.append(image_mp)

            if len(pending_tensors) >= batch_size:
                _flush_batch()

        _flush_batch()

        indexed_results.sort(key=lambda x: x[0])
        return [result for _, result in indexed_results]

    # ------------------------------------------------------------------
    # Core inference (single image tensor)
    # ------------------------------------------------------------------

    def _inference_with_confidence(
        self, image: "torch.Tensor"
    ) -> tuple[list[str], list[float]]:
        """Custom inference that also returns per-tag confidence scores."""
        results = self._batch_inference_with_confidence(image)
        return results[0]

    def _batch_inference_with_confidence(
        self, images: "torch.Tensor"
    ) -> list[tuple[list[str], list[float]]]:
        """Batch inference returning per-tag confidence scores for each image.

        Args:
            images: Tensor of shape (B, C, H, W).

        Returns:
            List of (tags_en, confidences) tuples, one per image.
        """
        import torch
        model = self.model

        image_embeds = model.image_proj(model.visual_encoder(images))
        image_atts = torch.ones(
            image_embeds.size()[:-1], dtype=torch.long
        ).to(images.device)

        image_cls_embeds = image_embeds[:, 0, :]

        bs = image_embeds.shape[0]
        des_per_class = int(model.label_embed.shape[0] / model.num_class)

        image_cls_embeds_norm = image_cls_embeds / image_cls_embeds.norm(
            dim=-1, keepdim=True
        )
        reweight_scale = model.reweight_scale.exp()
        logits_per_image = reweight_scale * image_cls_embeds_norm @ model.label_embed.t()
        logits_per_image = logits_per_image.view(bs, -1, des_per_class)

        weight_normalized = torch.nn.functional.softmax(logits_per_image, dim=2)
        label_embed_reweight = torch.empty(
            bs, model.num_class, 512
        ).to(images.device).to(images.dtype)

        for i in range(bs):
            reshaped_value = model.label_embed.view(-1, des_per_class, 512)
            product = weight_normalized[i].unsqueeze(-1) * reshaped_value
            label_embed_reweight[i] = product.sum(dim=1)

        label_embed = torch.nn.functional.relu(
            model.wordvec_proj(label_embed_reweight)
        )

        tagging_embed = model.tagging_head(
            encoder_embeds=label_embed,
            encoder_hidden_states=image_embeds,
            encoder_attention_mask=image_atts,
            return_dict=False,
            mode="tagging",
        )

        logits = model.fc(tagging_embed[0]).squeeze(-1)
        probs = torch.sigmoid(logits)

        # Apply per-class thresholds from the model, or user override
        if self.threshold != DEFAULT_THRESHOLD:
            class_threshold = torch.ones(model.num_class, device=images.device) * self.threshold
        else:
            class_threshold = model.class_threshold.to(images.device)

        targets = (probs > class_threshold).float()
        tag_array = targets.cpu().numpy()
        prob_array = probs.cpu().numpy()

        # Zero out delete indices
        tag_array[:, model.delete_tag_index] = 0

        results: list[tuple[list[str], list[float]]] = []

        for b in range(bs):
            indices = np.argwhere(tag_array[b] == 1).flatten()
            tokens_en = model.tag_list[indices].tolist()
            scores = prob_array[b][indices].tolist()

            # Sort by confidence descending
            combined = sorted(
                zip(tokens_en, scores),
                key=lambda x: x[1],
                reverse=True,
            )

            tags_en: list[str] = []
            confs: list[float] = []

            if combined:
                t_en, s = zip(*combined)
                tags_en = list(t_en)
                confs = [round(float(c), 4) for c in s]

            results.append((tags_en, confs))

        return results
