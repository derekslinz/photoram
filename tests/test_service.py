"""Tests for service-layer post-processing behavior."""

from __future__ import annotations

from pathlib import Path

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


def test_batch_mode_emits_incremental_progress_updates() -> None:
    class _FakeModel:
        device = "cpu"

        def tag_images(self, image_paths, batch_size: int = 1):
            return [
                TagResult(path=str(p), tags=["label"], confidences=[0.9])
                for p in image_paths
            ]

    svc = TaggingService(batch_size=2)
    svc._model = _FakeModel()  # type: ignore[assignment]

    paths = [Path("a.jpg"), Path("b.jpg"), Path("c.jpg")]
    events: list[tuple[str, int, int]] = []

    def _on_progress(path: Path, current: int, total: int) -> None:
        events.append((path.name, current, total))

    result = svc.tag_files(paths, on_progress=_on_progress)

    assert len(result.results) == 3
    assert events[0] == ("a.jpg", 0, 3)
    assert [e[1] for e in events[1:]] == [1, 2, 3]
    assert events[-1][2] == 3
