"""Tests for photoram.model behavior and safeguards."""

from __future__ import annotations

import types
import math
import sys

import pytest
from PIL import Image

import photoram.model as model_mod
from photoram.model import ImageNet21KModel, RAMPlusModel


def test_ramplusmodel_alias_points_to_imagenet21k_model() -> None:
    assert RAMPlusModel is ImageNet21KModel


def test_extract_id2label_normalizes_string_keys_and_underscores() -> None:
    fake_model = types.SimpleNamespace(
        config=types.SimpleNamespace(
            id2label={"0": "great_white_shark", 1: "mountain_bike"},
            num_labels=2,
        )
    )

    id2label = ImageNet21KModel._extract_id2label(fake_model)

    assert id2label[0] == "great white shark"
    assert id2label[1] == "mountain bike"


def test_extract_id2label_falls_back_to_class_indices() -> None:
    fake_model = types.SimpleNamespace(
        config=types.SimpleNamespace(
            id2label={},
            num_labels=3,
        )
    )

    id2label = ImageNet21KModel._extract_id2label(fake_model)

    assert id2label == {0: "class_0", 1: "class_1", 2: "class_2"}


def test_load_image_tensor_rejects_decompression_bomb(monkeypatch: pytest.MonkeyPatch) -> None:
    model = ImageNet21KModel.__new__(ImageNet21KModel)

    def _raise_bomb(_path):
        raise Image.DecompressionBombError("too many pixels")

    monkeypatch.setattr(model_mod.Image, "open", _raise_bomb)

    tensor, mp, err = model._load_image_tensor("evil.jpg")
    assert tensor is None
    assert mp is None
    assert err is not None
    assert "rejected for safety" in err.lower()


def test_batch_inference_applies_top_k_and_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Tensor:
        def __init__(self, data):
            self.data = data

        @property
        def shape(self):
            rows = len(self.data)
            cols = len(self.data[0]) if rows else 0
            return (rows, cols)

        def tolist(self):
            return self.data

    class _NoGrad:
        def __enter__(self):
            return None

        def __exit__(self, *_args):
            return False

    def _softmax(tensor: _Tensor, dim: int = -1) -> _Tensor:
        assert dim == -1
        rows = []
        for row in tensor.data:
            exps = [math.exp(x) for x in row]
            total = sum(exps)
            rows.append([x / total for x in exps])
        return _Tensor(rows)

    def _topk(tensor: _Tensor, k: int, dim: int = -1) -> tuple[_Tensor, _Tensor]:
        assert dim == -1
        top_values = []
        top_indices = []
        for row in tensor.data:
            ranked = sorted(enumerate(row), key=lambda item: item[1], reverse=True)[:k]
            top_indices.append([idx for idx, _ in ranked])
            top_values.append([val for _, val in ranked])
        return _Tensor(top_values), _Tensor(top_indices)

    fake_torch = types.SimpleNamespace(
        no_grad=lambda: _NoGrad(),
        softmax=_softmax,
        topk=_topk,
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    class _FakeProcessor:
        def __call__(self, *, images, return_tensors: str):
            assert return_tensors == "pt"
            class _DeviceValue:
                def to(self, _device):
                    return self

            return {"pixel_values": _DeviceValue()}

    class _FakeClassifier:
        def __call__(self, **kwargs):
            # 1 image x 4 classes
            logits = _Tensor([[5.0, 4.0, 0.0, -1.0]])
            return types.SimpleNamespace(logits=logits)

    model = ImageNet21KModel.__new__(ImageNet21KModel)
    model.device = "cpu"
    model.top_k = 3
    model.threshold = 0.03
    model._processor = _FakeProcessor()
    model._model = _FakeClassifier()
    model._id2label = {
        0: "alpha",
        1: "beta",
        2: "gamma",
        3: "delta",
    }

    results = model._batch_inference_with_confidence([Image.new("RGB", (4, 4))])

    assert len(results) == 1
    tags, confidences = results[0]
    assert tags == ["alpha", "beta"]
    assert len(confidences) == 2
    assert confidences[0] > confidences[1]


def test_tag_images_streams_by_batch_size() -> None:
    model = ImageNet21KModel.__new__(ImageNet21KModel)

    paths = [f"img_{i}.jpg" for i in range(5)]

    def _load(_path):
        return object(), 1.0, None

    batch_sizes: list[int] = []

    def _infer(images):
        batch_sizes.append(len(images))
        return [(["class_a"], [0.99]) for _ in images]

    model._load_image_tensor = _load  # type: ignore[assignment]
    model._batch_inference_with_confidence = _infer  # type: ignore[assignment]

    results = model.tag_images(paths, batch_size=2)

    assert batch_sizes == [2, 2, 1]
    assert [r.path for r in results] == paths
