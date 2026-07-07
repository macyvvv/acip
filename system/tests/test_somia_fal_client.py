from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pytest

from system.scripts.somia import fal_client
from system.scripts.somia.providers import VideoGenerationError


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_api_key_requires_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOMIA_VIDEO_API_KEY", raising=False)
    with pytest.raises(VideoGenerationError, match="SOMIA_VIDEO_API_KEY"):
        fal_client.api_key()


def test_await_result_polls_until_completed(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = iter([
        json.dumps({"status": "IN_QUEUE"}).encode("utf-8"),
        json.dumps({"status": "IN_PROGRESS"}).encode("utf-8"),
        json.dumps({"status": "COMPLETED"}).encode("utf-8"),
        json.dumps({"done": True}).encode("utf-8"),
    ])

    def fake_urlopen(request, timeout=None):  # noqa: ANN001
        return _FakeResponse(next(responses))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda _seconds: None)
    result = fal_client.await_result("https://x/status", "https://x/result", "test-key", poll_interval_seconds=0)
    assert result == {"done": True}


def test_await_result_raises_on_unexpected_status(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request, timeout=None):  # noqa: ANN001
        return _FakeResponse(json.dumps({"status": "ERROR"}).encode("utf-8"))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(VideoGenerationError, match="Unexpected fal.ai status"):
        fal_client.await_result("https://x/status", "https://x/result", "test-key")


def test_await_result_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request, timeout=None):  # noqa: ANN001
        return _FakeResponse(json.dumps({"status": "IN_QUEUE"}).encode("utf-8"))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr("time.sleep", lambda _seconds: None)
    with pytest.raises(VideoGenerationError, match="Timed out"):
        fal_client.await_result("https://x/status", "https://x/result", "test-key", poll_interval_seconds=0, timeout_seconds=0)


def test_upload_returns_access_url(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []

    def fake_urlopen(request, timeout=None):  # noqa: ANN001
        url = request.full_url if hasattr(request, "full_url") else request
        calls.append(url)
        if "storage/auth/token" in url:
            assert request.data == b"{}"  # fal rejects a bodyless POST here with 422
            return _FakeResponse(json.dumps({"token": "tok-123", "base_url": "https://v3b.fal.media"}).encode("utf-8"))
        if url == "https://v3b.fal.media/files/upload":
            assert request.get_header("Authorization") == "Bearer tok-123"
            return _FakeResponse(json.dumps({"access_url": "https://v3b.fal.media/files/abc.png"}).encode("utf-8"))
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    image_path = tmp_path / "ref.png"
    image_path.write_bytes(b"fake-image-bytes")
    access_url = fal_client.upload(image_path, "test-key")
    assert access_url == "https://v3b.fal.media/files/abc.png"
    assert any("storage/auth/token" in c for c in calls)
