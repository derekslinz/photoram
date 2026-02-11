"""Tests for photoram.schemas — result types and serialization."""

from __future__ import annotations

from photoram.schemas import BatchResult, TagResult


class TestTagResult:
    def test_success_property(self) -> None:
        r = TagResult(path="a.jpg", tags=["tree"], confidences=[0.9])
        assert r.success is True

    def test_error_property(self) -> None:
        r = TagResult(path="a.jpg", tags=[], error="bad file")
        assert r.success is False

    def test_to_dict_minimal(self) -> None:
        r = TagResult(path="a.jpg", tags=["tree", "sky"], confidences=[0.9, 0.8])
        d = r.to_dict()
        assert d["file"] == "a.jpg"
        assert d["tags"] == ["tree", "sky"]
        assert d["confidences"] == [0.9, 0.8]
        assert "tags_chinese" not in d
        assert "error" not in d

    def test_to_dict_with_chinese(self) -> None:
        r = TagResult(
            path="a.jpg", tags=["tree"], tags_chinese=["树"],
            confidences=[0.9],
        )
        d = r.to_dict(include_chinese=True)
        assert d["tags_chinese"] == ["树"]

    def test_to_dict_without_confidences(self) -> None:
        r = TagResult(path="a.jpg", tags=["tree"], confidences=[0.9])
        d = r.to_dict(include_confidences=False)
        assert "confidences" not in d

    def test_to_dict_with_error(self) -> None:
        r = TagResult(path="a.jpg", tags=[], error="corrupt")
        d = r.to_dict()
        assert d["error"] == "corrupt"


class TestBatchResult:
    def test_always_returns_list(self) -> None:
        """JSON contract: always a list, even for one result."""
        batch = BatchResult(results=[
            TagResult(path="a.jpg", tags=["tree"], confidences=[0.9]),
        ])
        data = batch.to_list()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_multiple_results(self) -> None:
        batch = BatchResult(results=[
            TagResult(path="a.jpg", tags=["tree"], confidences=[0.9]),
            TagResult(path="b.jpg", tags=["sky"], confidences=[0.8]),
        ])
        data = batch.to_list()
        assert len(data) == 2

    def test_succeeded_and_failed(self) -> None:
        batch = BatchResult(results=[
            TagResult(path="a.jpg", tags=["tree"], confidences=[0.9]),
            TagResult(path="b.jpg", tags=[], error="bad"),
        ])
        assert len(batch.succeeded) == 1
        assert len(batch.failed) == 1

    def test_empty_batch(self) -> None:
        batch = BatchResult()
        assert batch.to_list() == []
