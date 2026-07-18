#!/usr/bin/env python3
"""Two-stage keyframe generation for content 0007, built after four
consecutive single-stage attempts each sacrificed a different required
element (scene, outfit, face/earring) due to Illustrious-XL/SDXL's ~75
effective token budget per generation.

Stage 1: a tight character portrait -- face, earring, hair gradient,
outfit -- with the ENTIRE token budget available for identity, no scene
tags competing for attention.

Stage 2: fal-ai/lora/inpaint extends the canvas around that portrait
(scaled down, padded onto a larger canvas with a mask) to compose the
window/curtain/sea scene -- a separate generation call with its own full
token budget available for scene description, using the same checkpoint
so style stays consistent.

Both endpoints confirmed live via fal.ai's own docs before writing this:
fal-ai/lora (text-to-image, already used) and fal-ai/lora/inpaint
(image_url + mask_url + model_name + prompt).

Real fal.ai spend: 1 portrait generation + 1 inpaint generation per
attempt. Run from repo root:
PYTHONPATH=platform .venv/bin/python
businesses/somia/content/CONTENT/0007/render_two_stage.py
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
TEXT2IMG_RUNNER = "fal-ai/lora"
INPAINT_RUNNER = "fal-ai/lora/inpaint"
MODEL_NAME = "https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0/resolve/main/Illustrious-XL-v2.0.safetensors"
GUIDANCE_SCALE = 7.5

NEGATIVE_PROMPT = (
    "photorealistic, photo, 3d, western cartoon, disney, pixar, low quality, worst quality, "
    "bad anatomy, blurry, jpeg artifacts, nsfw, nudity, sexual content, revealing clothing, "
    "cleavage, exposed skin emphasis, bare shoulder, off shoulder, exposed collarbone, "
    "tank top, camisole, thin straps, sleeveless, revealing neckline, child, loli, school "
    "uniform, sailor collar, sailor fuku, neck ribbon, ribbon, bow, bowtie, necktie, "
    "buttons, button front, double breasted, lace collar, frilled collar, ruffled collar, "
    "choker, high collar shirt, blazer, age indicators, direct eye contact, confrontational "
    "expression, flat colors, minimalist, abstract, poster art, silhouette, graphic design, "
    "solid color background, uniform single-tone hair, black hair, brown eyes, no earring, "
    "heavy makeup, sharp features, generic face, indoor artificial lighting, empty room, "
    "abandoned space, horror atmosphere, dark atmosphere, heavy decoration, flashy colors, "
    "excessive ornamentation, text, watermark, caption, logo, UI, letters, words, subtitles, "
    "border, frame, chart, diagram, sketch lines, monochrome, grid, collage, multiple panels"
)

# Stage 1: identity only, no scene tags at all -- full token budget spent
# on face/earring/hair/outfit fidelity per TRANSCRIPTION.md.
# "roots" (bare word) triggered a garbled-text-label artifact on the first
# attempt -- SDXL-family checkpoints can misread short ambiguous words as
# a caption/label to render literally, especially combined with a number
# like "0.3". Reworded to avoid standalone trigger words; simplified the
# earring to a single small teardrop (the reference's actual design, not
# a dangling multi-gem drop) and strengthened the dark-to-light hair
# contrast language.
# 2026-07-18: re-checked directly against somia_nao01.png/somia_nao02.png
# (not the prior written transcription alone) after stage1_portrait.png
# rendered a sailor-collar/ribbon/button-front school top. The bare word
# "cardigan" is what did it -- on this checkpoint's Danbooru-tag training
# set, "cardigan" alone co-occurs heavily with school-uniform layering
# (sailor collar, neck ribbon, blazer buttons), so it pulled that whole
# cluster in even with no scene tags competing for budget. The reference
# art itself shows no cardigan structure at all: every panel on both
# sheets is a loose, soft, sheer/gauze blouse with wide draped sleeves,
# no buttons, no collar hardware, no ribbon -- described directly on the
# sheet as "薄絹素材" (thin sheer fabric that lets light through). Dropped
# "cardigan" and "high neckline" (the latter likely pulling the
# lace/ruffle choker-collar look), replaced with tags matching what the
# sheets actually show, and moved the excluded garment details into
# NEGATIVE_PROMPT per Rule 1 of the Illustrious-XL prompting skill.
PORTRAIT_PROMPT = (
    "1girl, solo, adult woman, portrait, upper body, delicate soft face, gentle round blue "
    "eyes, soft eyebrows, delicate fine linework, long straight hair, deep navy blue hair at "
    "top blending to pale sky blue at the ends, two tone blue hair, single small blue "
    "teardrop earring, loose soft blouse, wide loose sleeves, soft draped sheer fabric, "
    "covered shoulders, round modest neckline, pale ice-blue and white top, illustration, "
    "anime style, clean plain background"
)

# Stage 2: scene only -- the portrait's identity is already fixed pixel
# data by this point, so no identity tags compete for token budget here.
SCENE_PROMPT = (
    "open window, window frame, sheer white curtain blowing in wind, ocean view, sea, sky, "
    "high-key natural lighting, illustration, anime style, seamless background"
)


def generate_portrait() -> Path:
    key = fal_client.api_key()
    checkpoint = CONTENT_DIR / ".fal_checkpoint_portrait.json"
    submission = fal_client.submit_resumable(
        TEXT2IMG_RUNNER,
        {
            "model_name": MODEL_NAME,
            "prompt": PORTRAIT_PROMPT,
            "negative_prompt": NEGATIVE_PROMPT,
            "guidance_scale": GUIDANCE_SCALE,
        },
        key,
        checkpoint,
    )
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    url = result["images"][0]["url"]
    path = CONTENT_DIR / "stage1_portrait.png"
    fal_client.download(url, path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"stage1 portrait: {path}")
    return path


def build_canvas_and_mask(portrait_path: Path) -> tuple[Path, Path]:
    """Scale the portrait down and center it on a larger canvas, with a
    matching mask (white = generate new content here, black = preserve
    existing pixels -- standard SD inpainting mask convention)."""
    canvas_path = CONTENT_DIR / "stage2_canvas.png"
    mask_path = CONTENT_DIR / "stage2_mask.png"
    # Portrait scaled to 640x640, centered on a 1024x1024 canvas -> 192px
    # border on all sides for the outpainted scene.
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(portrait_path),
            "-vf", "scale=640:640,pad=1024:1024:192:192:color=white",
            str(canvas_path),
        ],
        check=True, capture_output=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=white:size=1024x1024",
            "-vf", "drawbox=x=192:y=192:w=640:h=640:color=black:t=fill",
            "-frames:v", "1", "-update", "1",
            str(mask_path),
        ],
        check=True, capture_output=True,
    )
    print(f"canvas: {canvas_path}, mask: {mask_path}")
    return canvas_path, mask_path


def generate_scene(canvas_path: Path, mask_path: Path) -> Path:
    key = fal_client.api_key()
    canvas_url = fal_client.upload(canvas_path, key)
    mask_url = fal_client.upload(mask_path, key)
    checkpoint = CONTENT_DIR / ".fal_checkpoint_scene.json"
    submission = fal_client.submit_resumable(
        INPAINT_RUNNER,
        {
            "model_name": MODEL_NAME,
            "image_url": canvas_url,
            "mask_url": mask_url,
            "prompt": SCENE_PROMPT,
            "negative_prompt": NEGATIVE_PROMPT,
            "guidance_scale": GUIDANCE_SCALE,
        },
        key,
        checkpoint,
    )
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    url = result["images"][0]["url"]
    path = CONTENT_DIR / "stage2_composed.png"
    fal_client.download(url, path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"stage2 composed: {path}")
    return path


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    portrait_path = generate_portrait()
    canvas_path, mask_path = build_canvas_and_mask(portrait_path)
    generate_scene(canvas_path, mask_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
