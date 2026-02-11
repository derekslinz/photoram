"""Formalized result schemas for photoram output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TagResult:
    """Result for a single image tagging operation.

    This is the canonical result type used by all output writers.
    """

    path: str
    tags: list[str]
    confidences: list[float] = field(default_factory=list)
    error: Optional[str] = None
    image_megapixels: Optional[float] = None

    @property
    def success(self) -> bool:
        """Whether tagging succeeded for this image."""
        return self.error is None

    def to_dict(
        self,
        include_confidences: bool = True,
    ) -> dict:
        """Serialize to a JSON-compatible dict.

        The output shape is always consistent regardless of options.
        """
        d: dict = {
            "file": self.path,
            "tags": self.tags,
        }
        if include_confidences:
            d["confidences"] = self.confidences
        if self.error is not None:
            d["error"] = self.error
        return d


@dataclass
class BatchResult:
    """Result for a batch of image tagging operations.

    The JSON contract is: **always a list**, even for a single image.
    """

    results: list[TagResult] = field(default_factory=list)

    @property
    def succeeded(self) -> list[TagResult]:
        return [r for r in self.results if r.success]

    @property
    def failed(self) -> list[TagResult]:
        return [r for r in self.results if not r.success]

    def to_list(
        self,
        include_confidences: bool = True,
    ) -> list[dict]:
        """Serialize all results to a list of dicts.

        **Always returns a list**, even for a single result.
        This is the stable JSON output contract.
        """
        return [
            r.to_dict(
                include_confidences=include_confidences,
            )
            for r in self.results
        ]
