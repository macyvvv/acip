#!/usr/bin/env python3
"""One-off experimental test of fal-ai/ip-adapter-face-id as a candidate
fix for the token-budget wall documented in NOTES.md / the
writing-illustrious-xl-prompts skill: four consecutive single-stage
Illustrious-XL attempts each sacrificed a different required element
(scene, outfit, face/earring) because combined identity+scene tags
exceeded the ~75-token effective attention budget.

Idea: condition the face directly on Nao's reference image via IP-Adapter
instead of describing her face in prompt tokens at all -- frees up token
budget for hair gradient/earring/outfit/scene. This is NOT the same as
the two-stage portrait+outpaint approach (render_two_stage.py) -- this is
a single generation call with face conditioning, no separate outpaint
step.

Confirmed live via fal.ai's own OpenAPI schema before writing this
(https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/ip-adapter-face-id):
- face_image_url: reference face image, auto-scaled/cropped to 640x640
- model_type: must be "SDXL-v1" or "SDXL-v2-plus" to use an SDXL base
- base_sdxl_model_repo: free-text string, but loaded via HF's
  `from_pretrained(repo_id)` -- requires a bare "namespace/repo" id AND a
  diffusers-format repo (unet/, vae/, text_encoder*/, tokenizer*/,
  scheduler/, model_index.json), not a single-file .safetensors repo.
  First attempt used the full resolve-URL form of
  OnomaAIResearch/Illustrious-XL-v2.0 (the form used elsewhere in this
  pipeline for fal-ai/lora's `model_name`) and failed server-side with
  `huggingface_hub.errors.HFValidationError: Repo id must be in the form
  'repo_name' or 'namespace/repo_name'`. OnomaAIResearch's own repo is
  also single-file-only (confirmed via its file tree: just
  Illustrious-XL-v2.0.safetensors, no diffusers subfolders) -- a bare
  repo id wouldn't have worked either. Using a community diffusers-format
  reconversion instead: Bercraft/Illustrious-XL-v2.0-FP16-Diffusers
  (confirmed via its file tree to have the full diffusers structure).

This is a single cheap validation generation, not a production render.
Real fal.ai spend: 1 image generation.
Run from repo root: PYTHONPATH=platform .venv/bin/python
businesses/somia/content/CONTENT/0007/test_ip_adapter_face_id.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from system.core.dotenv import load_dotenv  # noqa: E402
from system.scripts.somia import fal_client  # noqa: E402

CONTENT_DIR = Path(__file__).resolve().parent
REF_DIR = CONTENT_DIR.parent / "ref_nao" / "character_sheets"
RUNNER = "fal-ai/ip-adapter-face-id"
MODEL_TYPE = "SDXL-v2-plus"
BASE_SDXL_MODEL_REPO = "Bercraft/Illustrious-XL-v2.0-FP16-Diffusers"
GUIDANCE_SCALE = 7.5

# No face/eye/eyebrow description here -- that's the point of this test.
# Only hair, earring, outfit, and scene tags, short and comma-separated
# per writing-illustrious-xl-prompts.
PROMPT = (
    "1girl, solo, adult woman, illustration, anime style, "
    "long straight hair, deep navy blue hair at top blending to pale sky blue at the ends, "
    "two tone blue hair, single small blue teardrop earring, "
    "soft long sleeve cardigan, covered shoulders, high neckline, pale ice-blue top, "
    "standing at open window, window frame, sheer white curtain blowing in wind, "
    "ocean view, sea, sky, high-key natural lighting"
)
NEGATIVE_PROMPT = (
    "photorealistic, photo, 3d, western cartoon, disney, pixar, low quality, worst quality, "
    "bad anatomy, blurry, jpeg artifacts, nsfw, nudity, sexual content, revealing clothing, "
    "cleavage, exposed skin emphasis, bare shoulder, off shoulder, exposed collarbone, "
    "tank top, camisole, thin straps, sleeveless, revealing neckline, child, loli, school "
    "uniform, age indicators, flat colors, minimalist, abstract, poster art, silhouette, "
    "graphic design, solid color background, uniform single-tone hair, black hair, brown "
    "eyes, no earring, heavy makeup, text, watermark, caption, logo, letters, words, border, "
    "frame, monochrome, grid, collage, multiple panels"
)


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    key = fal_client.api_key()

    face_path = REF_DIR / "somia_nao01.png"
    face_url = fal_client.upload(face_path, key)
    print(f"uploaded face reference: {face_url}")

    checkpoint = CONTENT_DIR / ".fal_checkpoint_ip_adapter_test.json"
    submission = fal_client.submit_resumable(
        RUNNER,
        {
            "prompt": PROMPT,
            "negative_prompt": NEGATIVE_PROMPT,
            "face_image_url": face_url,
            "model_type": MODEL_TYPE,
            "base_sdxl_model_repo": BASE_SDXL_MODEL_REPO,
            "guidance_scale": GUIDANCE_SCALE,
            "width": 1024,
            "height": 1024,
        },
        key,
        checkpoint,
    )
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    url = result["image"]["url"]
    out_path = CONTENT_DIR / "ip_adapter_test.png"
    fal_client.download(url, out_path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"ip-adapter test output: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
