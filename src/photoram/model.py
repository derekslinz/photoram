"""Model loading, caching, and inference for RAM++."""

from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Optional

import numpy as np

from .errors import CheckpointCorruptionError, CheckpointDownloadError, ModelError
from .schemas import TagResult

# Suppress timm deprecation warnings from the RAM package
warnings.filterwarnings("ignore", category=FutureWarning, module="timm")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HF_REPO_ID = "xinyu1205/recognize-anything-plus-model"
HF_FILENAME = "ram_plus_swin_large_14m.pth"

DEFAULT_IMAGE_SIZE = 384
DEFAULT_THRESHOLD = 0.68

# Minimum reasonable checkpoint size (100 MB) — guards against truncated downloads
_MIN_CHECKPOINT_BYTES = 100 * 1024 * 1024

CACHE_DIR = Path(os.environ.get(
    "PHOTORAM_CACHE",
    Path.home() / ".cache" / "photoram",
))


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
        self.image_size = image_size
        self.threshold = threshold

        try:
            self.pretrained_path = pretrained_path or str(self._ensure_checkpoint())
        except (CheckpointDownloadError, CheckpointCorruptionError):
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
    # Checkpoint download
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_checkpoint() -> Path:
        """Download the RAM++ checkpoint from HuggingFace if not cached."""
        dest = CACHE_DIR / HF_FILENAME

        if dest.exists():
            # Validate file isn't truncated / corrupted
            size = dest.stat().st_size
            if size < _MIN_CHECKPOINT_BYTES:
                raise CheckpointCorruptionError(
                    f"Cached checkpoint appears corrupted ({size:,} bytes).\n"
                    f"Delete and retry:\n"
                    f"  rm {dest}\n"
                    f"  photoram-cli info"
                )
            return dest

        CACHE_DIR.mkdir(parents=True, exist_ok=True)

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

        # Post-download validation
        if path.exists() and path.stat().st_size < _MIN_CHECKPOINT_BYTES:
            path.unlink(missing_ok=True)
            raise CheckpointCorruptionError(
                "Downloaded checkpoint appears truncated. Deleted and retrying may help:\n"
                f"  photoram-cli info"
            )

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
    # Single-image inference
    # ------------------------------------------------------------------

    def tag_image(self, image_path: str | Path) -> TagResult:
        """Run RAM++ on a single image and return tags with confidences."""
        import torch
        from PIL import Image

        try:
            image = self.transform(Image.open(image_path)).unsqueeze(0).to(self.device)
        except Exception as e:
            return TagResult(
                path=str(image_path),
                tags=[],
                tags_chinese=[],
                confidences=[],
                error=f"Failed to load image: {e}",
            )

        with torch.no_grad():
            tags_en, tags_zh, confidences = self._inference_with_confidence(image)

        return TagResult(
            path=str(image_path),
            tags=tags_en,
            tags_chinese=tags_zh,
            confidences=confidences,
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

        Args:
            image_paths: List of image file paths.
            batch_size: Number of images to process per forward pass.
                        Larger batches are faster on GPU but use more memory.

        Returns:
            List of TagResult, one per input image (order preserved).
        """
        import torch
        from PIL import Image

        # Pre-load and transform all images, tracking failures
        loaded: list[tuple[int, "torch.Tensor"]] = []
        failed: list[tuple[int, TagResult]] = []

        for idx, img_path in enumerate(image_paths):
            try:
                tensor = self.transform(Image.open(img_path)).to(self.device)
                loaded.append((idx, tensor))
            except Exception as e:
                failed.append((idx, TagResult(
                    path=str(img_path),
                    tags=[],
                    tags_chinese=[],
                    confidences=[],
                    error=f"Failed to load image: {e}",
                )))

        # Process in batches
        batch_results: list[tuple[int, TagResult]] = []
        for batch_start in range(0, len(loaded), batch_size):
            batch = loaded[batch_start:batch_start + batch_size]
            indices = [idx for idx, _ in batch]
            tensors = torch.stack([t for _, t in batch]).to(self.device)

            with torch.no_grad():
                batch_tags = self._batch_inference_with_confidence(tensors)

            for i, (tags_en, tags_zh, confs) in enumerate(batch_tags):
                batch_results.append((indices[i], TagResult(
                    path=str(image_paths[indices[i]]),
                    tags=tags_en,
                    tags_chinese=tags_zh,
                    confidences=confs,
                )))

        # Merge and sort by original index
        all_indexed = batch_results + failed
        all_indexed.sort(key=lambda x: x[0])
        return [r for _, r in all_indexed]

    # ------------------------------------------------------------------
    # Core inference (single image tensor)
    # ------------------------------------------------------------------

    def _inference_with_confidence(
        self, image: "torch.Tensor"
    ) -> tuple[list[str], list[str], list[float]]:
        """Custom inference that also returns per-tag confidence scores."""
        results = self._batch_inference_with_confidence(image)
        return results[0]

    def _batch_inference_with_confidence(
        self, images: "torch.Tensor"
    ) -> list[tuple[list[str], list[str], list[float]]]:
        """Batch inference returning per-tag confidence scores for each image.

        Args:
            images: Tensor of shape (B, C, H, W).

        Returns:
            List of (tags_en, tags_zh, confidences) tuples, one per image.
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

        results: list[tuple[list[str], list[str], list[float]]] = []

        for b in range(bs):
            indices = np.argwhere(tag_array[b] == 1).flatten()
            tokens_en = model.tag_list[indices].tolist()
            tokens_zh = model.tag_list_chinese[indices].tolist()
            scores = prob_array[b][indices].tolist()

            # Sort by confidence descending
            combined = sorted(
                zip(tokens_en, tokens_zh, scores),
                key=lambda x: x[2],
                reverse=True,
            )

            tags_en: list[str] = []
            tags_zh: list[str] = []
            confs: list[float] = []

            if combined:
                t_en, t_zh, s = zip(*combined)
                tags_en = list(t_en)
                tags_zh = list(t_zh)
                confs = [round(float(c), 4) for c in s]

            results.append((tags_en, tags_zh, confs))

        return results
