from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os

from system.scripts.somia import fal_client
from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import RenderResult, VideoGenerationProvider, register_provider

# Kling is also served through fal.ai's hosted queue API. Adopted after
# Pika 2.2 repeatedly drifted stylized/illustrated keyframes toward
# photorealism; Kling has a reputation for holding stylized/anime input
# images together better through motion.
KEYFRAME_MODEL = os.environ.get("SOMIA_KLING_KEYFRAME_MODEL", "fal-ai/flux/dev")
VIDEO_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"

DEFAULT_NEGATIVE_PROMPT = os.environ.get(
    "SOMIA_KLING_NEGATIVE_PROMPT",
    "blur, distort, low quality, photorealistic, photo, realistic skin texture, 3D render, live action",
)
# How strictly Kling follows the prompt vs. improvising motion (0-1).
DEFAULT_CFG_SCALE = float(os.environ.get("SOMIA_KLING_CFG_SCALE", "0.5"))

# Kling 2.5-turbo also only supports 5 or 10 second clips; same 12s spec
# mismatch as Pika, same closest-supported-duration default.
DEFAULT_DURATION_SECONDS = os.environ.get("SOMIA_KLING_DURATION", "10")


class KlingProvider(VideoGenerationProvider):
    """Two fal.ai calls: a text-to-image keyframe (flux), then Kling 2.5-turbo
    image-to-video animating that keyframe. Requires SOMIA_VIDEO_API_KEY
    (a fal.ai API key)."""

    name = "kling"

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
                "duration": DEFAULT_DURATION_SECONDS,
                "cfg_scale": DEFAULT_CFG_SCALE,
            },
            key,
        )
        video_result = fal_client.await_result(video_submission["status_url"], video_submission["response_url"], key)
        video_url = video_result["video"]["url"]
        video_path = output_dir / "video.mp4"
        fal_client.download(video_url, video_path)

        notes = (
            f"kling v2.5-turbo/pro, duration={DEFAULT_DURATION_SECONDS}s, cfg_scale={DEFAULT_CFG_SCALE}. "
            "Spec calls for a 12s clip; Kling only supports 5 or 10s, so this used the closest "
            "supported duration and does not include the spec's on-screen text overlay "
            "(add it in a separate compositing pass). Verify style consistency each render — "
            "not yet confirmed reliable across many samples."
        )
        return RenderResult(
            provider=self.name,
            model=f"{KEYFRAME_MODEL} + {VIDEO_MODEL}",
            keyframe_path=str(keyframe_path),
            video_path=str(video_path),
            rendered_at=datetime.now(timezone.utc).isoformat(),
            notes=notes,
        )


register_provider(KlingProvider)
