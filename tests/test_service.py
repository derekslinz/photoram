"""Tests for service-layer post-processing behavior."""

from __future__ import annotations

from photoram.schemas import TagResult
from photoram.service import TaggingService


def test_top_n_post_process_without_tags_chinese_attribute() -> None:
    svc = TaggingService(top_n=1)
    result = TagResult(
        path="image.jpg",
        tags=["tree", "sky"],
        confidences=[0.9, 0.8],
    )

    svc._post_process(result)

    assert result.tags == ["tree"]
    assert result.confidences == [0.9]
