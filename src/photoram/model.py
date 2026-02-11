"""Model loading, caching, and inference for RAM++."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from huggingface_hub import hf_hub_download
from PIL import Image

# RAM++ imports
from ram import get_transform
from ram.models import ram_plus

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HF_REPO_ID = "xinyu1205/recognize-anything-plus-model"
HF_FILENAME = "ram_plus_swin_large_14m.pth"

DEFAULT_IMAGE_SIZE = 384
DEFAULT_THRESHOLD = 0.5

CACHE_DIR = Path(os.environ.get(
    "PHOTORAM_CACHE",
    Path.home() / ".cache" / "photoram",
))


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TagResult:
    """Result for a single image."""

    path: str
    tags: list[str]
    tags_chinese: list[str]
    confidences: list[float]


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
        self.device = self._resolve_device(device)
        self.pretrained_path = pretrained_path or str(self._ensure_checkpoint())
        self.transform = get_transform(image_size=self.image_size)

        self._model: Optional[torch.nn.Module] = None

    # ------------------------------------------------------------------
    # Device resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_device(device: Optional[str]) -> torch.device:
        if device:
            return torch.device(device)
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
            return dest

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        downloaded = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_FILENAME,
            local_dir=str(CACHE_DIR),
            local_dir_use_symlinks=False,
        )
        return Path(downloaded)

    # ------------------------------------------------------------------
    # Lazy model loading
    # ------------------------------------------------------------------

    @property
    def model(self) -> torch.nn.Module:
        if self._model is None:
            self._model = ram_plus(
                pretrained=self.pretrained_path,
                image_size=self.image_size,
                vit="swin_l",
            )
            self._model.eval()
            self._model = self._model.to(self.device)
        return self._model

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def tag_image(self, image_path: str | Path) -> TagResult:
        """Run RAM++ on a single image and return tags with confidences."""
        image = self.transform(Image.open(image_path)).unsqueeze(0).to(self.device)

        with torch.no_grad():
            tags_en, tags_zh, confidences = self._inference_with_confidence(image)

        return TagResult(
            path=str(image_path),
            tags=tags_en,
            tags_chinese=tags_zh,
            confidences=confidences,
        )

    def _inference_with_confidence(
        self, image: torch.Tensor
    ) -> tuple[list[str], list[str], list[float]]:
        """Custom inference that also returns per-tag confidence scores."""
        model = self.model

        image_embeds = model.image_proj(model.visual_encoder(image))
        image_atts = torch.ones(
            image_embeds.size()[:-1], dtype=torch.long
        ).to(image.device)

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
        ).to(image.device).to(image.dtype)

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

        # Apply per-class thresholds
        class_threshold = model.class_threshold.to(image.device)

        # Override with our global threshold if different from default
        if self.threshold != 0.68:
            class_threshold = torch.ones(model.num_class, device=image.device) * self.threshold

        targets = (probs > class_threshold).float()
        tag_array = targets.cpu().numpy()
        prob_array = probs.cpu().numpy()

        # Zero out delete indices
        tag_array[:, model.delete_tag_index] = 0

        tags_en: list[str] = []
        tags_zh: list[str] = []
        confs: list[float] = []

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
            if combined:
                t_en, t_zh, s = zip(*combined)
                tags_en = list(t_en)
                tags_zh = list(t_zh)
                confs = [round(float(c), 4) for c in s]

        return tags_en, tags_zh, confs
