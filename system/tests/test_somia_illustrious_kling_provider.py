from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pytest

from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import VideoGenerationError, get_provider
from system.scripts.somia.providers_illustrious_kling import IllustriousKlingProvider


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
        image_prompt="1girl, solo, dark room, monitor glow, star hairpin",
        negative_prompt="",
        animation_instruction="Glances toward the screen, expression softens slightly",
        camera_instruction="Medium close-up, steady, no sudden zoom",
        on_screen_text="Still watching, even now.",
        audio_notes="soft room tone",
    )


def _fake_urlopen_factory():
    calls: list[str] = []
    payloads: dict[str, dict] = {}

    def fake_urlopen(request, timeout=None):  # noqa: ANN001
        url = request.full_url if hasattr(request, "full_url") else request
        calls.append(url)
        if getattr(request, "data", None):
            payloads[url] = json.loads(request.data.decode("utf-8"))
        if url == "https://queue.fal.run/fal-ai/lora":
            return _json_response({
                "request_id": "kf-1",
                "status_url": "https://queue.fal.run/fal-ai/lora/requests/kf-1/status",
                "response_url": "https://queue.fal.run/fal-ai/lora/requests/kf-1",
            })
        if url == "https://queue.fal.run/fal-ai/lora/requests/kf-1/status":
            return _json_response({"status": "COMPLETED"})
        if url == "https://queue.fal.run/fal-ai/lora/requests/kf-1":
            return _json_response({"images": [{"url": "https://cdn.example/keyframe.png"}]})
        if url == "https://cdn.example/keyframe.png":
            return _FakeResponse(b"keyframe-bytes")
        if url == "https://queue.fal.run/fal-ai/kling-video/v2.5-turbo/pro/image-to-video":
            return _json_response({
                "request_id": "vid-1",
                "status_url": "https://queue.fal.run/fal-ai/kling-video/v2.5-turbo/pro/image-to-video/requests/vid-1/status",
                "response_url": "https://queue.fal.run/fal-ai/kling-video/v2.5-turbo/pro/image-to-video/requests/vid-1",
            })
        if url == "https://queue.fal.run/fal-ai/kling-video/v2.5-turbo/pro/image-to-video/requests/vid-1/status":
            return _json_response({"status": "COMPLETED"})
        if url == "https://queue.fal.run/fal-ai/kling-video/v2.5-turbo/pro/image-to-video/requests/vid-1":
            return _json_response({"video": {"url": "https://cdn.example/video.mp4"}})
        if url == "https://cdn.example/video.mp4":
            return _FakeResponse(b"video-bytes")
        raise AssertionError(f"unexpected URL requested: {url}")

    return fake_urlopen, calls, payloads


def test_illustrious_kling_requires_api_key(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SOMIA_VIDEO_API_KEY", raising=False)
    provider = IllustriousKlingProvider()
    with pytest.raises(VideoGenerationError, match="SOMIA_VIDEO_API_KEY"):
        provider.generate(_spec(), tmp_path)


def test_illustrious_kling_generates_keyframe_and_video(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SOMIA_VIDEO_API_KEY", "test-key")
    fake_urlopen, calls, payloads = _fake_urlopen_factory()
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    provider = IllustriousKlingProvider()
    result = provider.generate(_spec(), tmp_path)

    assert Path(result.keyframe_path).read_bytes() == b"keyframe-bytes"
    assert Path(result.video_path).read_bytes() == b"video-bytes"
    assert result.provider == "illustrious_kling"
    assert "OnomaAIResearch/Illustrious-XL-v2.0" in result.model
    assert calls.index("https://queue.fal.run/fal-ai/lora") < calls.index(
        "https://queue.fal.run/fal-ai/kling-video/v2.5-turbo/pro/image-to-video"
    )
    keyframe_payload = payloads["https://queue.fal.run/fal-ai/lora"]
    assert keyframe_payload["model_name"].endswith("Illustrious-XL-v2.0.safetensors")
    assert keyframe_payload["prompt"] == _spec().image_prompt
    # empty spec.negative_prompt falls back to the module default
    assert "disney" in keyframe_payload["negative_prompt"]


def test_illustrious_kling_uses_spec_negative_prompt_when_present(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SOMIA_VIDEO_API_KEY", "test-key")
    fake_urlopen, calls, payloads = _fake_urlopen_factory()
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    spec = ContentSpec(
        content_id="0001",
        character="Airi",
        image_prompt="1girl, solo",
        negative_prompt="sitting upright, composed expression, smiling",
        animation_instruction="glances at viewer",
        camera_instruction="steady",
        on_screen_text="Still here.",
        audio_notes="",
    )
    provider = IllustriousKlingProvider()
    provider.generate(spec, tmp_path)
    keyframe_payload = payloads["https://queue.fal.run/fal-ai/lora"]
    assert keyframe_payload["negative_prompt"] == "sitting upright, composed expression, smiling"


def test_get_provider_lazily_loads_illustrious_kling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOMIA_VIDEO_API_KEY", "test-key")
    provider = get_provider("illustrious_kling")
    assert isinstance(provider, IllustriousKlingProvider)
