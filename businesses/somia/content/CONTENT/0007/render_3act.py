#!/usr/bin/env python3
"""One-off chaining script for content 0007's 30s/3-act version (see
prompt.md). NOT a generalized pipeline feature yet -- render_content.py's
providers only support single ~10s clips. If chaining proves valuable
across more episodes, this logic belongs in
platform/system/scripts/somia/ as a real provider; premature to build
that abstraction from a single use.

Real fal.ai spend: 1 keyframe generation + 3 Kling video generations.
Run from repo root: PYTHONPATH=platform .venv/bin/python
businesses/somia/content/CONTENT/0007/render_3act.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from system.core.dotenv import load_dotenv  # noqa: E402
from system.scripts.somia import fal_client  # noqa: E402

CONTENT_DIR = Path(__file__).resolve().parent
KEYFRAME_RUNNER = "fal-ai/lora"
KEYFRAME_MODEL_NAME = "https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0/resolve/main/Illustrious-XL-v2.0.safetensors"
VIDEO_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"
GUIDANCE_SCALE = 7.5
CFG_SCALE = 0.4  # lowered from 0.5 default per the staged-prompt experiment (prompt.md)
DURATION = "10"

# Illustrious-XL/Danbooru-family checkpoints need short comma-separated tags,
# not prose, and their CLIP text encoder does not understand grammatical
# negation -- writing "NOT a tank top" in the POSITIVE prompt tends to add
# "tank top" as a concept rather than exclude it. Every excluded concept
# below lives only in NEGATIVE_PROMPT as a short tag; the positive prompt
# (BASE_DESC etc.) states only what should be present, never what shouldn't.
# Lesson learned live this session: a first attempt with prose + in-prompt
# negations produced a broken, flat/abstract keyframe -- confirms this is a
# real constraint, not a style preference.
NEGATIVE_PROMPT = (
    "photorealistic, photo, 3d, western cartoon, disney, pixar, low quality, worst quality, "
    "bad anatomy, blurry, jpeg artifacts, nsfw, nudity, sexual content, revealing clothing, "
    "cleavage, exposed skin emphasis, bare shoulder, off shoulder, exposed collarbone, "
    "tank top, camisole, thin straps, sleeveless, revealing neckline, child, loli, school "
    "uniform, age indicators, direct eye contact, confrontational expression, flat colors, "
    "minimalist, abstract, poster art, silhouette, graphic design, solid color background, "
    "uniform single-tone hair, black hair, brown eyes, no earring, heavy makeup, sharp "
    "features, generic face, indoor artificial lighting, empty room, abandoned space, "
    "horror atmosphere, dark atmosphere, heavy decoration, flashy colors, excessive "
    "ornamentation, text, watermark, caption, logo, UI, letters, words, subtitles, border, "
    "frame, chart, diagram, sketch lines, monochrome, grid, collage, multiple panels"
)
KLING_NEGATIVE_PROMPT = "blur, distort, low quality, photorealistic, photo, realistic skin texture, 3D render, live action"

# Positive-only, terse tags. Hair gradient and earring/outfit are stated as
# concrete positive facts, not as "not X" corrections. Outfit corrected
# 2026-07-18 (operator): NOT off-shoulder -- a thin, soft cardigan-like
# covered top, minimal exposure, per TRANSCRIPTION.md's cross-check of
# both reference sheets (only 1-2 of 10+ panels show any incidental
# shoulder drape; none show a deliberately shoulder-baring cut).
# "Delicate" (繊細) linework/features added per the same transcription --
# explicit art-direction language from the reference sheets' own detail
# notes, not just a generic "detailed" tag.
# Kept short deliberately: CLIP's effective attention window is ~75 tokens.
# The first attempt at this trimmed BASE_DESC was still too long combined
# with per-act scene/pose tags -- later tokens (profile view, window/
# curtain/ocean scene) got diluted/ignored, producing a close-up portrait
# against a flat background instead of the intended window scene. Fixed by
# (a) trimming BASE_DESC to identity-only essentials, (b) putting each
# act's scene+pose tags FIRST in the combined prompt, character-identity
# tags after -- scene/pose changes per act and must survive if anything
# gets truncated; identity tags are more forgiving.
# v5.2 (same day): even the scene-first reorder still overflowed the
# effective token budget once both scene tags AND identity tags were
# present -- covered-shoulder/cardigan got dropped this time, reverting
# to a sleeveless dress. Cut ruthlessly instead of reordering again:
# every tag below is load-bearing (caused a real, observed defect when
# missing in some prior attempt); nothing decorative/redundant kept.
BASE_DESC = (
    "dark navy roots pale blue tips gradient hair, blue teardrop earring, long sleeve "
    "cardigan, covered shoulders, high neckline"
)

ACT1_IMAGE_PROMPT = (
    "1girl, solo, adult woman, profile view, at open window, curtain, sea, sky, wind, "
    f"{BASE_DESC}"
)
ACT1_MOTION = (
    "A genuinely held presence establishing the situation clearly (a woman at a coastal "
    "window, present and calm) -- the full 10s spent on stillness: hair, curtain (separate "
    "from her clothing), and the sheer-knit top's fabric all move continuously in the wind, "
    "a slow real breath, a barely-there weight shift. The blue teardrop earring stays "
    "visible and catches ambient light naturally throughout. She does not know or register "
    "the viewer during this act. No turn, no acknowledgment. Static-to-subtle-push medium "
    "shot from just outside the window looking toward her profile; no cuts."
)

ACT2_MOTION = (
    "Slight anticipation lag before the head turn (gaze flicks toward camera fractionally "
    "before head follows) beginning 1-2s into this clip, completing into a small incomplete "
    "acknowledging smile by 4-5s. Hold the acknowledgment for several seconds (5-8s). Begin "
    "the turn back at 8s, and this turn-back motion should be clearly, meaningfully underway "
    "(not just starting) by the very last frame of this clip. She does not step closer, does "
    "not extend a hand -- stays framed by the window, glass/threshold still between her and "
    "the viewer. At the turn (2-3s into this clip), one coordinated light event with two "
    "facets, both brief and resolving immediately: (a) the light through the window curtain "
    "and off the sea ripples/refracts, as if caught off guard with her, for a fraction of a "
    "second -- a natural-world disturbance, NOT a digital glitch; (b) simultaneously, a small "
    "glint/flare catches the blue teardrop earring. Two facets of one event, not two stacked "
    "effects -- combined prominence should stay subtle, in-world light behavior, not a filter "
    "over the image. Static-to-subtle-push medium shot, no cuts, camera holds through the turn."
)

ACT3_MOTION = (
    "HARD CONSTRAINT: she does not look at or turn toward the camera again at any point in "
    "this clip, under any circumstance. This clip is the continuation and completion of the "
    "turn-away motion already in progress at the start -- not a new beat, not a fresh "
    "reaction, not a second acknowledgment. The turn completes into full profile by 3s into "
    "this clip. Gaze settles outward toward the sea. Wind gradually settles through the "
    "remainder of the clip. Final frame should read as visually close to the very start of "
    "the sequence: same pose, same framing, in profile (not frontal), gaze at the sea (not "
    "at camera), blue earring visible -- the loop point. Do not introduce any new expression "
    "change, glance, or motion toward the viewer in this clip. Static-to-subtle-push medium "
    "shot, no cuts."
)


def generate_keyframe() -> Path:
    key = fal_client.api_key()
    checkpoint = CONTENT_DIR / ".fal_checkpoint_act1_keyframe.json"
    submission = fal_client.submit_resumable(
        KEYFRAME_RUNNER,
        {
            "model_name": KEYFRAME_MODEL_NAME,
            "prompt": ACT1_IMAGE_PROMPT,
            "negative_prompt": NEGATIVE_PROMPT,
            "guidance_scale": GUIDANCE_SCALE,
        },
        key,
        checkpoint,
    )
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    keyframe_url = result["images"][0]["url"]
    keyframe_path = CONTENT_DIR / "keyframe.png"
    fal_client.download(keyframe_url, keyframe_path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"keyframe: {keyframe_path}")
    return keyframe_path


def generate_video_from_image(image_url_or_path: str, motion_prompt: str, act_name: str) -> Path:
    key = fal_client.api_key()
    if not image_url_or_path.startswith("http"):
        image_url = fal_client.upload(image_url_or_path, key)
    else:
        image_url = image_url_or_path
    checkpoint = CONTENT_DIR / f".fal_checkpoint_{act_name}_video.json"
    submission = fal_client.submit_resumable(
        VIDEO_MODEL,
        {
            "image_url": image_url,
            "prompt": motion_prompt,
            "negative_prompt": KLING_NEGATIVE_PROMPT,
            "duration": DURATION,
            "cfg_scale": CFG_SCALE,
        },
        key,
        checkpoint,
    )
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=600)
    video_url = result["video"]["url"]
    video_path = CONTENT_DIR / f"{act_name}.mp4"
    fal_client.download(video_url, video_path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"{act_name}: {video_path}")
    return video_path


def extract_last_frame(video_path: Path, out_path: Path) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-sseof", "-0.1", "-i", str(video_path), "-update", "1", "-frames:v", "1", str(out_path)],
        check=True,
        capture_output=True,
    )
    return out_path


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")

    keyframe_path = generate_keyframe()

    act1_path = generate_video_from_image(str(keyframe_path), ACT1_MOTION, "act1")
    act1_last_frame = extract_last_frame(act1_path, CONTENT_DIR / "act1_last_frame.png")

    act2_path = generate_video_from_image(str(act1_last_frame), ACT2_MOTION, "act2")
    act2_last_frame = extract_last_frame(act2_path, CONTENT_DIR / "act2_last_frame.png")

    act3_path = generate_video_from_image(str(act2_last_frame), ACT3_MOTION, "act3")

    concat_list = CONTENT_DIR / "concat_list.txt"
    concat_list.write_text(
        f"file '{act1_path.name}'\nfile '{act2_path.name}'\nfile '{act3_path.name}'\n", encoding="utf-8"
    )
    combined_path = CONTENT_DIR / "video_30s.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(combined_path)],
        check=True,
        cwd=CONTENT_DIR,
    )
    print(f"combined 30s video: {combined_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
