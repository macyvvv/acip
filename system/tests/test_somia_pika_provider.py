from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pytest

from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import VideoGenerationError, get_provider
from system.scripts.somia.providers_pika import PikaProvider


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def _json_response(payload: dict) -> _FakeResponse:
    return _FakeResponse(json.dumps(payload).encode("utf-8"))


def _spec() -> ContentSpec:
    return ContentSpec(
        content_id="0001",
        character="Airi",
        image_prompt="Airi, cool blue palette, dim corridor",
        animation_instruction="Minimal motion, single gaze shift",
        camera_instruction="Extreme close-up, slow zoom out",
        on_screen_text="You noticed too late that she was already there.",
        audio_notes="soft ambient bed",
    )


def _fake_urlopen_factory():
    calls: list[str] = []

    def fake_urlopen(request, timeout=None):  # noqa: ANN001
        url = request.full_url if hasattr(request, "full_url") else request
        calls.append(url)
        if url == "https://queue.fal.run/fal-ai/flux/schnell":
            return _json_response({
                "request_id": "kf-1",
                "status_url": "https://queue.fal.run/fal-ai/flux/schnell/requests/kf-1/status",
                "response_url": "https://queue.fal.run/fal-ai/flux/schnell/requests/kf-1",
            })
        if url == "https://queue.fal.run/fal-ai/flux/schnell/requests/kf-1/status":
            return _json_response({"status": "COMPLETED"})
        if url == "https://queue.fal.run/fal-ai/flux/schnell/requests/kf-1":
            return _json_response({"images": [{"url": "https://cdn.example/keyframe.png"}]})
        if url == "https://cdn.example/keyframe.png":
            return _FakeResponse(b"keyframe-bytes")
        if url == "https://queue.fal.run/fal-ai/pika/v2.2/image-to-video":
            return _json_response({
                "request_id": "vid-1",
                "status_url": "https://queue.fal.run/fal-ai/pika/v2.2/image-to-video/requests/vid-1/status",
                "response_url": "https://queue.fal.run/fal-ai/pika/v2.2/image-to-video/requests/vid-1",
            })
        if url == "https://queue.fal.run/fal-ai/pika/v2.2/image-to-video/requests/vid-1/status":
            return _json_response({"status": "COMPLETED"})
        if url == "https://queue.fal.run/fal-ai/pika/v2.2/image-to-video/requests/vid-1":
            return _json_response({"video": {"url": "https://cdn.example/video.mp4"}})
        if url == "https://cdn.example/video.mp4":
            return _FakeResponse(b"video-bytes")
        raise AssertionError(f"unexpected URL requested: {url}")

    return fake_urlopen, calls


def test_pika_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SOMIA_VIDEO_API_KEY", raising=False)
    provider = PikaProvider()
    with pytest.raises(VideoGenerationError, match="SOMIA_VIDEO_API_KEY"):
        provider.generate(_spec(), tmp_path)


def test_pika_provider_generates_keyframe_and_video(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SOMIA_VIDEO_API_KEY", "test-key")
    fake_urlopen, calls = _fake_urlopen_factory()
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = PikaProvider()
    result = provider.generate(_spec(), tmp_path)

    assert Path(result.keyframe_path).read_bytes() == b"keyframe-bytes"
    assert Path(result.video_path).read_bytes() == b"video-bytes"
    assert result.provider == "pika"
    assert "fal-ai/flux/schnell" in result.model
    assert "fal-ai/pika/v2.2/image-to-video" in result.model
    assert "12s" in result.notes and "10" in result.notes
    # keyframe generated before the video call uses its URL as input
    assert calls.index("https://queue.fal.run/fal-ai/flux/schnell") < calls.index("https://queue.fal.run/fal-ai/pika/v2.2/image-to-video")


def test_pika_provider_raises_on_http_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import io
    import urllib.error

    monkeypatch.setenv("SOMIA_VIDEO_API_KEY", "test-key")

    def fake_urlopen(request, timeout=None):  # noqa: ANN001
        raise urllib.error.HTTPError(request.full_url, 401, "Unauthorized", None, io.BytesIO(b"unauthorized"))

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    provider = PikaProvider()
    with pytest.raises(VideoGenerationError, match="401"):
        provider.generate(_spec(), tmp_path)


def test_get_provider_lazily_loads_pika(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOMIA_VIDEO_API_KEY", "test-key")
    provider = get_provider("pika")
    assert isinstance(provider, PikaProvider)
