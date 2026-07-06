from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import time
import urllib.error
import urllib.request

from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import RenderResult, VideoGenerationError, VideoGenerationProvider, register_provider

# Pika is served through fal.ai's hosted queue API (Pika no longer runs its own
# public API directly). Same auth/queue pattern is reused for the keyframe
# image step (flux) and the image-to-video step (pika).
FAL_QUEUE_BASE = "https://queue.fal.run"
KEYFRAME_MODEL = os.environ.get("SOMIA_PIKA_KEYFRAME_MODEL", "fal-ai/flux/schnell")
VIDEO_MODEL = "fal-ai/pika/v2.2/image-to-video"

# Pika v2.2 only supports 5 or 10 second clips; somia's 12-second format spec
# does not map onto it exactly. Default to the closest supported duration (10s)
# rather than silently rendering a mismatched clip without saying so.
DEFAULT_DURATION_SECONDS = os.environ.get("SOMIA_PIKA_DURATION", "10")
DEFAULT_RESOLUTION = os.environ.get("SOMIA_PIKA_RESOLUTION", "720p")

DEFAULT_POLL_INTERVAL_SECONDS = 3
DEFAULT_TIMEOUT_SECONDS = 300


def _api_key() -> str:
    key = os.environ.get("SOMIA_VIDEO_API_KEY", "").strip()
    if not key:
        raise VideoGenerationError("SOMIA_VIDEO_API_KEY is not set (required for the pika provider).")
    return key


def _fal_request(method: str, url: str, api_key: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise VideoGenerationError(f"fal.ai request failed ({exc.code}) for {url}: {body}") from exc


def _submit(model_id: str, payload: dict, api_key: str) -> dict:
    return _fal_request("POST", f"{FAL_QUEUE_BASE}/{model_id}", api_key, payload)


def _await_result(
    status_url: str,
    response_url: str,
    api_key: str,
    *,
    poll_interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict:
    deadline = time.monotonic() + timeout_seconds
    while True:
        status_payload = _fal_request("GET", status_url, api_key)
        status = status_payload.get("status")
        if status == "COMPLETED":
            return _fal_request("GET", response_url, api_key)
        if status not in {"IN_QUEUE", "IN_PROGRESS"}:
            raise VideoGenerationError(f"Unexpected fal.ai status '{status}' for {status_url}: {status_payload}")
        if time.monotonic() >= deadline:
            raise VideoGenerationError(f"Timed out after {timeout_seconds}s waiting on {status_url}")
        time.sleep(poll_interval_seconds)


def _download(url: str, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as response:
        dest_path.write_bytes(response.read())


class PikaProvider(VideoGenerationProvider):
    """Two fal.ai calls: a text-to-image keyframe (flux), then Pika 2.2
    image-to-video animating that keyframe. Requires SOMIA_VIDEO_API_KEY
    (a fal.ai API key)."""

    name = "pika"

    def generate(self, spec: ContentSpec, output_dir: Path) -> RenderResult:
        api_key = _api_key()
        output_dir.mkdir(parents=True, exist_ok=True)

        keyframe_submission = _submit(KEYFRAME_MODEL, {"prompt": spec.image_prompt}, api_key)
        keyframe_result = _await_result(keyframe_submission["status_url"], keyframe_submission["response_url"], api_key)
        keyframe_url = keyframe_result["images"][0]["url"]
        keyframe_path = output_dir / "keyframe.png"
        _download(keyframe_url, keyframe_path)

        motion_prompt = " ".join(part for part in (spec.animation_instruction, spec.camera_instruction) if part)
        video_submission = _submit(
            VIDEO_MODEL,
            {
                "image_url": keyframe_url,
                "prompt": motion_prompt,
                "duration": int(DEFAULT_DURATION_SECONDS),
                "resolution": DEFAULT_RESOLUTION,
            },
            api_key,
        )
        video_result = _await_result(video_submission["status_url"], video_submission["response_url"], api_key)
        video_url = video_result["video"]["url"]
        video_path = output_dir / "video.mp4"
        _download(video_url, video_path)

        notes = (
            f"pika v2.2, duration={DEFAULT_DURATION_SECONDS}s/resolution={DEFAULT_RESOLUTION}. "
            "Spec calls for a 12s clip; Pika only supports 5 or 10s, so this used the closest "
            "supported duration and does not include the spec's on-screen text overlay "
            "(add it in a separate compositing pass)."
        )
        return RenderResult(
            provider=self.name,
            model=f"{KEYFRAME_MODEL} + {VIDEO_MODEL}",
            keyframe_path=str(keyframe_path),
            video_path=str(video_path),
            rendered_at=datetime.now(timezone.utc).isoformat(),
            notes=notes,
        )


register_provider(PikaProvider)
