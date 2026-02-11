"""Tests for photoram.model safeguards."""

from __future__ import annotations

import hashlib
import types
import warnings
from pathlib import Path

import pytest
from PIL import Image

import photoram.model as model_mod
from photoram.errors import CheckpointCorruptionError, CheckpointIntegrityError
from photoram.model import DEFAULT_IMAGE_SIZE, RAMPlusModel


def test_resolve_ram_image_size_allows_supported_values() -> None:
    assert RAMPlusModel._resolve_ram_image_size(224) == 224
    assert RAMPlusModel._resolve_ram_image_size(384) == 384


def test_resolve_ram_image_size_falls_back_for_unsupported_values() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        resolved = RAMPlusModel._resolve_ram_image_size(512)

    assert resolved == DEFAULT_IMAGE_SIZE
    assert any("vision_config_path" in str(w.message) for w in caught)


def test_validate_checkpoint_rejects_small_file(tmp_path: Path) -> None:
    candidate = tmp_path / "small.pth"
    candidate.write_bytes(b"x" * 16)

    with pytest.raises(CheckpointCorruptionError):
        RAMPlusModel._validate_checkpoint(candidate)


def test_validate_checkpoint_rejects_hash_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = tmp_path / "checkpoint.pth"
    candidate.write_bytes(b"trusted-model-bytes")

    monkeypatch.setattr(model_mod, "_MIN_CHECKPOINT_BYTES", 1)
    monkeypatch.setattr(model_mod, "HF_CHECKPOINT_SHA256", "0" * 64)

    with pytest.raises(CheckpointIntegrityError):
        RAMPlusModel._validate_checkpoint(candidate)


def test_ensure_checkpoint_rejects_tampered_cached_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    filename = "model.pth"
    candidate = tmp_path / filename
    candidate.write_bytes(b"tampered")

    monkeypatch.setattr(model_mod, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(model_mod, "HF_FILENAME", filename)
    monkeypatch.setattr(model_mod, "_MIN_CHECKPOINT_BYTES", 1)
    monkeypatch.setattr(model_mod, "HF_CHECKPOINT_SHA256", "f" * 64)

    with pytest.raises(CheckpointIntegrityError):
        RAMPlusModel._ensure_checkpoint()


def test_ensure_checkpoint_deletes_bad_download(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    filename = "model.pth"
    downloaded_path = tmp_path / filename

    monkeypatch.setattr(model_mod, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(model_mod, "HF_FILENAME", filename)
    monkeypatch.setattr(model_mod, "_MIN_CHECKPOINT_BYTES", 1)

    # Force a hash mismatch for the downloaded artifact.
    monkeypatch.setattr(model_mod, "HF_CHECKPOINT_SHA256", "a" * 64)

    fake_hf_hub = types.SimpleNamespace()

    def _fake_download(*args, **kwargs) -> str:
        downloaded_path.write_bytes(b"definitely-not-the-right-checkpoint")
        return str(downloaded_path)

    fake_hf_hub.hf_hub_download = _fake_download
    monkeypatch.setitem(__import__("sys").modules, "huggingface_hub", fake_hf_hub)

    with pytest.raises(CheckpointIntegrityError):
        RAMPlusModel._ensure_checkpoint()

    assert not downloaded_path.exists(), "Failed integrity downloads should be deleted"


def test_load_image_tensor_rejects_decompression_bomb(monkeypatch: pytest.MonkeyPatch) -> None:
    model = RAMPlusModel.__new__(RAMPlusModel)
    model.device = "cpu"

    class _DummyTensor:
        def to(self, device: str):
            return self

    model.transform = lambda _: _DummyTensor()

    def _raise_bomb(_path):
        raise Image.DecompressionBombError("too many pixels")

    monkeypatch.setattr(model_mod.Image, "open", _raise_bomb)

    tensor, mp, err = model._load_image_tensor("evil.jpg")
    assert tensor is None
    assert mp is None
    assert err is not None
    assert "rejected for safety" in err.lower()


def test_validate_checkpoint_accepts_matching_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "checkpoint.pth"
    payload = b"legit-checkpoint-bytes"
    candidate.write_bytes(payload)

    monkeypatch.setattr(model_mod, "_MIN_CHECKPOINT_BYTES", 1)
    monkeypatch.setattr(model_mod, "HF_CHECKPOINT_SHA256", hashlib.sha256(payload).hexdigest())

    # Should not raise.
    RAMPlusModel._validate_checkpoint(candidate)
