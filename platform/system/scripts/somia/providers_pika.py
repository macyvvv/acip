from __future__ import annotations

from pathlib import Path
import os

from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import RenderResult, VideoGenerationProvider, register_provider
from system.scripts.somia.providers_fal_common import FluxVideoVendorConfig, generate_via_flux_keyframe_and_vendor_video

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
# just a prompt-tuning gap — see platform/system/platform/scripts/somia/providers_kling.py
# for the alternative adopted after this kept recurring.
DEFAULT_NEGATIVE_PROMPT = os.environ.get(
    "SOMIA_PIKA_NEGATIVE_PROMPT",
    "photorealistic, photo, realistic skin texture, 3D render, live action, camera flash",
)

# Pika v2.2 only supports 5 or 10 second clips; somia's 12-second format spec
# does not map onto it exactly. Default to the closest supported duration (10s)
# rather than silently rendering a mismatched clip without saying so.
DEFAULT_DURATION_SECONDS = int(os.environ.get("SOMIA_PIKA_DURATION", "10"))
DEFAULT_RESOLUTION = os.environ.get("SOMIA_PIKA_RESOLUTION", "720p")


class PikaProvider(VideoGenerationProvider):
    """Two fal.ai calls: a text-to-image keyframe (flux), then Pika 2.2
    image-to-video animating that keyframe. Requires SOMIA_VIDEO_API_KEY
    (a fal.ai API key). Kept available for comparison; kling is the
    currently recommended provider (see providers_kling.py) after Pika's
    style-drift issue kept recurring in testing."""

    name = "pika"

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
                    "resolution": DEFAULT_RESOLUTION,
                },
                known_caveat="style-drift toward photorealism was observed and is not reliably prevented by negative_prompt",
            ),
        )


register_provider(PikaProvider)
