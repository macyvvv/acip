from __future__ import annotations

from pathlib import Path
import os

from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import RenderResult, VideoGenerationProvider, register_provider
from system.scripts.somia.providers_fal_common import FluxVideoVendorConfig, generate_via_flux_keyframe_and_vendor_video

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
        return generate_via_flux_keyframe_and_vendor_video(
            spec,
            output_dir,
            FluxVideoVendorConfig(
                provider_name=self.name,
                keyframe_model=KEYFRAME_MODEL,
                video_model=VIDEO_MODEL,
                negative_prompt=DEFAULT_NEGATIVE_PROMPT,
                rendered_duration_seconds=DEFAULT_DURATION_SECONDS,
                video_extra_payload={
                    "duration": DEFAULT_DURATION_SECONDS,
                    "cfg_scale": DEFAULT_CFG_SCALE,
                },
                known_caveat="style consistency not yet confirmed reliable across many samples",
            ),
        )


register_provider(KlingProvider)
