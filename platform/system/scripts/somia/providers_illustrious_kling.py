from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os

from system.scripts.somia import fal_client
from system.scripts.somia.content_spec import ContentSpec
from system.scripts.somia.prompt_budget import check_prompt_budget
from system.scripts.somia.providers import RenderResult, VideoGenerationProvider, register_provider

# flux/dev (general-purpose, Western-trained) read as "Disney-style" in
# testing and did not produce the intended Japanese illustration register.
# Illustrious-XL is trained on Danbooru2023 (Japanese anime/illustration
# tag data) and is run through fal.ai's generic SDXL+LoRA runner rather
# than a dedicated flux endpoint.
#
# model_name must be the direct .safetensors file URL, not the bare HF repo
# id — fal-ai/lora tried to load the repo id as a multi-file diffusers repo
# and failed with "does not contain a config.json or model_index.json".
# The first call against a given checkpoint URL also cold-starts a ~7GB
# download on fal's side and can take several minutes; subsequent calls
# should be faster once fal has it cached.
KEYFRAME_RUNNER = "fal-ai/lora"
KEYFRAME_MODEL_NAME = os.environ.get(
    "SOMIA_ILLUSTRIOUS_MODEL_NAME",
    "https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0/resolve/main/Illustrious-XL-v2.0.safetensors",
)
VIDEO_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"

# Confirmed in testing: Illustrious/Danbooru-family checkpoints need
# Danbooru-style comma-separated tags, not natural-language prose. A prose
# prompt produced visibly rougher/lower-quality output than the same scene
# described as tags. Write image_prompt as tags for this provider.
DEFAULT_NEGATIVE_PROMPT = os.environ.get(
    "SOMIA_ILLUSTRIOUS_NEGATIVE_PROMPT",
    "photorealistic, photo, 3d, western cartoon, disney, pixar, low quality, worst quality",
)
DEFAULT_GUIDANCE_SCALE = float(os.environ.get("SOMIA_ILLUSTRIOUS_GUIDANCE_SCALE", "7.5"))

DEFAULT_KLING_NEGATIVE_PROMPT = os.environ.get(
    "SOMIA_KLING_NEGATIVE_PROMPT",
    "blur, distort, low quality, photorealistic, photo, realistic skin texture, 3D render, live action",
)
DEFAULT_KLING_CFG_SCALE = float(os.environ.get("SOMIA_KLING_CFG_SCALE", "0.5"))
DEFAULT_DURATION_SECONDS = os.environ.get("SOMIA_KLING_DURATION", "10")

# A cold checkpoint download was observed taking longer than the shared
# fal_client default (600s); give the keyframe step more headroom.
KEYFRAME_TIMEOUT_SECONDS = int(os.environ.get("SOMIA_ILLUSTRIOUS_TIMEOUT_SECONDS", "900"))


class IllustriousKlingProvider(VideoGenerationProvider):
    """Keyframe via Illustrious-XL (Danbooru-trained, Japanese illustration
    register) through fal.ai's generic LoRA/checkpoint runner, animated with
    Kling 2.5-turbo image-to-video. Requires SOMIA_VIDEO_API_KEY (a fal.ai
    API key)."""

    name = "illustrious_kling"

    def generate(self, spec: ContentSpec, output_dir: Path) -> RenderResult:
        check_prompt_budget(spec.image_prompt, label="illustrious_kling image_prompt")
        key = fal_client.api_key()
        output_dir.mkdir(parents=True, exist_ok=True)

        keyframe_checkpoint = output_dir / ".fal_checkpoint_illustrious_kling_keyframe.json"
        keyframe_submission = fal_client.submit_resumable(
            KEYFRAME_RUNNER,
            {
                "model_name": KEYFRAME_MODEL_NAME,
                "prompt": spec.image_prompt,
                "negative_prompt": spec.negative_prompt or DEFAULT_NEGATIVE_PROMPT,
                "guidance_scale": DEFAULT_GUIDANCE_SCALE,
                # Without this, fal.ai hard-truncates prompts at ~77 CLIP
                # tokens instead of chunking/averaging past it (confirmed
                # against fal.ai's own fal-ai/lora API docs, 2026-07-19) --
                # discovered via Yui's portrait regeneration failures; see
                # businesses/somia/content/BRAND/PORTRAIT_METHODOLOGY.md.
                "prompt_weighting": True,
            },
            key,
            keyframe_checkpoint,
        )
        keyframe_result = fal_client.await_result(
            keyframe_submission["status_url"],
            keyframe_submission["response_url"],
            key,
            timeout_seconds=KEYFRAME_TIMEOUT_SECONDS,
        )
        keyframe_url = keyframe_result["images"][0]["url"]
        keyframe_path = output_dir / "keyframe.png"
        fal_client.download(keyframe_url, keyframe_path)
        fal_client.clear_checkpoint(keyframe_checkpoint)

        motion_prompt = " ".join(part for part in (spec.animation_instruction, spec.camera_instruction) if part)
        video_checkpoint = output_dir / ".fal_checkpoint_illustrious_kling_video.json"
        video_submission = fal_client.submit_resumable(
            VIDEO_MODEL,
            {
                "image_url": keyframe_url,
                "prompt": motion_prompt,
                "negative_prompt": DEFAULT_KLING_NEGATIVE_PROMPT,
                "duration": DEFAULT_DURATION_SECONDS,
                "cfg_scale": DEFAULT_KLING_CFG_SCALE,
            },
            key,
            video_checkpoint,
        )
        video_result = fal_client.await_result(video_submission["status_url"], video_submission["response_url"], key)
        video_url = video_result["video"]["url"]
        video_path = output_dir / "video.mp4"
        fal_client.download(video_url, video_path)
        fal_client.clear_checkpoint(video_checkpoint)

        spec_deviations = (
            f"duration: spec requested 12s, rendered {DEFAULT_DURATION_SECONDS}s (Kling caps at 10s)",
            "on_screen_text: not composited into the video (requires a separate compositing pass)",
            "prompting: this checkpoint needs Danbooru-tag-style prompts (comma-separated tags, "
            "not prose) to render cleanly -- write image_prompt accordingly",
        )
        notes = (
            f"keyframe={KEYFRAME_MODEL_NAME} via {KEYFRAME_RUNNER}, video=kling v2.5-turbo/pro "
            f"duration={DEFAULT_DURATION_SECONDS}s. " + " ".join(spec_deviations)
        )
        return RenderResult(
            provider=self.name,
            model=f"{KEYFRAME_MODEL_NAME} ({KEYFRAME_RUNNER}) + {VIDEO_MODEL}",
            keyframe_path=str(keyframe_path),
            video_path=str(video_path),
            rendered_at=datetime.now(timezone.utc).isoformat(),
            notes=notes,
            spec_deviations=spec_deviations,
        )


register_provider(IllustriousKlingProvider)
