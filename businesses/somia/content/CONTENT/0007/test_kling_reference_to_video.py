#!/usr/bin/env python3
"""One-off experimental test of fal-ai/kling-video/o1/reference-to-video as
a candidate fix for the token-budget wall documented in NOTES.md / the
writing-illustrious-xl-prompts skill.

Idea, genuinely different from every prior attempt on this content: skip
the SDXL/Illustrious-XL keyframe generation step entirely. Instead of
describing Nao's face/hair/earring/outfit in prompt tokens (which
competes with scene/pose tokens for the ~75-token effective budget),
condition the VIDEO model directly on a reference portrait image via
Kling O1's "elements" identity-locking mechanism, and spend the entire
text prompt on scene/motion/camera only.

Confirmed live via fal.ai's own OpenAPI schema before writing this
(https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/kling-video/o1/reference-to-video):
- elements: array of {frontal_image_url (required), reference_image_urls
  (required, 1-3 images)} -- referenced in the prompt as @Element1 etc.
- prompt: natural language, references elements/images by @-tag
- UNVERIFIED: whether this identity-locking mechanism works well on
  illustration/anime-style reference images specifically (docs make no
  style-specific claims either way) -- this is exactly what this test
  validates.
- Using stage1_portrait.png (already-validated clean single portrait from
  render_two_stage.py's Stage 1) as both frontal_image_url and the sole
  reference_image_urls entry, since we don't yet have multiple distinct
  angle shots of Nao as separate clean images -- the raw character
  reference sheets are multi-panel collages, not single-subject images,
  and would likely confuse this endpoint's element-conditioning.

This is a single cheap validation generation (5s, cheapest duration), not
a production render. Real fal.ai spend: 1 video generation, ~$0.56 at
$0.112/sec for 5s.
Run from repo root: PYTHONPATH=platform .venv/bin/python
businesses/somia/content/CONTENT/0007/test_kling_reference_to_video.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "platform"))

from system.core.dotenv import load_dotenv  # noqa: E402
from system.scripts.somia import fal_client  # noqa: E402

CONTENT_DIR = Path(__file__).resolve().parent
RUNNER = "fal-ai/kling-video/o1/reference-to-video"

# Identity carried entirely by @Element1 (the reference portrait) -- this
# prompt spends its full budget on scene/motion/camera only, no face/hair/
# earring/outfit description at all. This is the core of the test.
PROMPT = (
    "@Element1 standing at an open window, sheer white curtain blowing in the wind beside her, "
    "ocean view through the window, sea and sky visible, profile view looking outward at the sea, "
    "gentle calm expression, wind moving through her hair, high-key natural lighting, "
    "a slow held breath, barely-there weight shift, static medium shot, no cuts, anime illustration style"
)


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    key = fal_client.api_key()

    portrait_path = CONTENT_DIR / "stage1_portrait.png"
    portrait_url = fal_client.upload(portrait_path, key)
    print(f"uploaded reference portrait: {portrait_url}")

    checkpoint = CONTENT_DIR / ".fal_checkpoint_kling_ref_test.json"
    submission = fal_client.submit_resumable(
        RUNNER,
        {
            "prompt": PROMPT,
            "elements": [
                {
                    "frontal_image_url": portrait_url,
                    "reference_image_urls": [portrait_url],
                }
            ],
            "duration": "5",
            "aspect_ratio": "9:16",
        },
        key,
        checkpoint,
    )
    result = fal_client.await_result(submission["status_url"], submission["response_url"], key, timeout_seconds=900)
    url = result["video"]["url"]
    out_path = CONTENT_DIR / "kling_reference_test.mp4"
    fal_client.download(url, out_path)
    fal_client.clear_checkpoint(checkpoint)
    print(f"kling reference-to-video test output: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
