from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from system.scripts.somia import fal_client
from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.providers import RenderResult

# Shared by every fal-hosted "flux keyframe -> image-to-video vendor" provider
# (providers_pika.py, providers_kling.py). These two were near-identical
# copies (same two-call shape, same motion-prompt join, same notes assembly)
# differing only in model ids and vendor-specific video params -- collapsed
# here so a third vendor adapter doesn't have to re-copy the whole flow.

SPEC_DURATION_SECONDS = 12  # somia's format spec; no current vendor supports it


@dataclass(frozen=True)
class FluxVideoVendorConfig:
    provider_name: str
    keyframe_model: str
    video_model: str
    negative_prompt: str
    rendered_duration_seconds: int | str
    video_extra_payload: dict
    # A short, vendor-specific caveat appended to notes/spec_deviations
    # (e.g. "style consistency not yet confirmed reliable across many
    # samples"). Optional -- pass "" if there's nothing vendor-specific to add.
    known_caveat: str = ""


def generate_via_flux_keyframe_and_vendor_video(
    spec: ContentSpec, output_dir: Path, config: FluxVideoVendorConfig
) -> RenderResult:
    key = fal_client.api_key()
    output_dir.mkdir(parents=True, exist_ok=True)

    keyframe_checkpoint = output_dir / f".fal_checkpoint_{config.provider_name}_keyframe.json"
    keyframe_submission = fal_client.submit_resumable(
        config.keyframe_model, {"prompt": spec.image_prompt}, key, keyframe_checkpoint
    )
    keyframe_result = fal_client.await_result(keyframe_submission["status_url"], keyframe_submission["response_url"], key)
    keyframe_url = keyframe_result["images"][0]["url"]
    keyframe_path = output_dir / "keyframe.png"
    fal_client.download(keyframe_url, keyframe_path)
    fal_client.clear_checkpoint(keyframe_checkpoint)

    motion_prompt = " ".join(part for part in (spec.animation_instruction, spec.camera_instruction) if part)
    video_payload = {
        "image_url": keyframe_url,
        "prompt": motion_prompt,
        "negative_prompt": config.negative_prompt,
        **config.video_extra_payload,
    }
    video_checkpoint = output_dir / f".fal_checkpoint_{config.provider_name}_video.json"
    video_submission = fal_client.submit_resumable(config.video_model, video_payload, key, video_checkpoint)
    video_result = fal_client.await_result(video_submission["status_url"], video_submission["response_url"], key)
    video_url = video_result["video"]["url"]
    video_path = output_dir / "video.mp4"
    fal_client.download(video_url, video_path)
    fal_client.clear_checkpoint(video_checkpoint)

    spec_deviations = [
        f"duration: spec requested {SPEC_DURATION_SECONDS}s, rendered {config.rendered_duration_seconds}s "
        "(vendor does not support the spec duration)",
        "on_screen_text: not composited into the video (requires a separate compositing pass)",
    ]
    if config.known_caveat:
        spec_deviations.append(config.known_caveat)

    notes = (
        f"{config.provider_name}: {config.video_model}, duration={config.rendered_duration_seconds}s. "
        + " ".join(spec_deviations)
    )

    return RenderResult(
        provider=config.provider_name,
        model=f"{config.keyframe_model} + {config.video_model}",
        keyframe_path=str(keyframe_path),
        video_path=str(video_path),
        rendered_at=datetime.now(timezone.utc).isoformat(),
        notes=notes,
        spec_deviations=tuple(spec_deviations),
    )
