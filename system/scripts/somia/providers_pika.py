from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os

from system.scripts.somia import fal_client
from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import RenderResult, VideoGenerationProvider, register_provider

# Pika is served through fal.ai's hosted queue API (Pika no longer runs its own
# public API directly). Same auth/queue pattern is reused for the keyframe
# image step (flux) and the image-to-video step (pika).
# flux/schnell is faster/cheaper but was observed dropping the character
# entirely from multi-concept prompts; flux/dev costs more but reliably
# renders the subject. Quality here matters more than the cost delta.
KEYFRAME_MODEL = os.environ.get("SOMIA_PIKA_KEYFRAME_MODEL", "fal-ai/flux/dev")
VIDEO_MODEL = "fal-ai/pika/v2.2/image-to-video"

# Observed failure mode: Pika 2.2 unreliably drifts a stylized/illustrated
# keyframe toward photorealism over the course of the clip, even with a
# negative_prompt set. This is a known limitation of this provider, not
# just a prompt-tuning gap — see system/scripts/somia/providers_kling.py
# for the alternative adopted after this kept recurring.
DEFAULT_NEGATIVE_PROMPT = os.environ.get(
    "SOMIA_PIKA_NEGATIVE_PROMPT",
    "photorealistic, photo, realistic skin texture, 3D render, live action, camera flash",
)

# Pika v2.2 only supports 5 or 10 second clips; somia's 12-second format spec
# does not map onto it exactly. Default to the closest supported duration (10s)
# rather than silently rendering a mismatched clip without saying so.
DEFAULT_DURATION_SECONDS = os.environ.get("SOMIA_PIKA_DURATION", "10")
DEFAULT_RESOLUTION = os.environ.get("SOMIA_PIKA_RESOLUTION", "720p")


class PikaProvider(VideoGenerationProvider):
    """Two fal.ai calls: a text-to-image keyframe (flux), then Pika 2.2
    image-to-video animating that keyframe. Requires SOMIA_VIDEO_API_KEY
    (a fal.ai API key). Kept available for comparison; kling is the
    currently recommended provider (see providers_kling.py) after Pika's
    style-drift issue kept recurring in testing."""

    name = "pika"

    def generate(self, spec: ContentSpec, output_dir: Path) -> RenderResult:
        key = fal_client.api_key()
        output_dir.mkdir(parents=True, exist_ok=True)

        keyframe_submission = fal_client.submit(KEYFRAME_MODEL, {"prompt": spec.image_prompt}, key)
        keyframe_result = fal_client.await_result(keyframe_submission["status_url"], keyframe_submission["response_url"], key)
        keyframe_url = keyframe_result["images"][0]["url"]
        keyframe_path = output_dir / "keyframe.png"
        fal_client.download(keyframe_url, keyframe_path)

        motion_prompt = " ".join(part for part in (spec.animation_instruction, spec.camera_instruction) if part)
        video_submission = fal_client.submit(
            VIDEO_MODEL,
            {
                "image_url": keyframe_url,
                "prompt": motion_prompt,
                "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
                "duration": int(DEFAULT_DURATION_SECONDS),
                "resolution": DEFAULT_RESOLUTION,
            },
            key,
        )
        video_result = fal_client.await_result(video_submission["status_url"], video_submission["response_url"], key)
        video_url = video_result["video"]["url"]
        video_path = output_dir / "video.mp4"
        fal_client.download(video_url, video_path)

        notes = (
            f"pika v2.2, duration={DEFAULT_DURATION_SECONDS}s/resolution={DEFAULT_RESOLUTION}. "
            "Spec calls for a 12s clip; Pika only supports 5 or 10s, so this used the closest "
            "supported duration and does not include the spec's on-screen text overlay "
            "(add it in a separate compositing pass). Style-drift toward photorealism was "
            "observed and is not reliably prevented by negative_prompt."
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
