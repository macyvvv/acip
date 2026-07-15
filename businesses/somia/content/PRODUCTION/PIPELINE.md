# Production Pipeline

## Validated 5-stage pipeline (what actually produced good results)

This is the flow that, after extensive testing on CONTENT/0001, produced
output matching the brand's intended register. Stages marked **[manual]**
were validated by hand but are **not yet wired into
`render_content.py`** — the code currently only does a simpler text→image
→video path (see "Current code state" below). Closing that gap is the main
open task for this pipeline.

1. **Keyframe via reference img2img** — `fal-ai/lora/image-to-image` with
   the Illustrious-XL checkpoint, using a cropped ChatGPT concept-sheet
   panel as the `image_url` at `noise_strength ≈ 0.45`, guided by the
   spec's Image Prompt (KV) in Danbooru tag form. **[manual]**
   - This is the single biggest quality lever. Text-only generation
     (no reference image) never captured the intended look; feeding the
     reference KV as an img2img base did.
2. **Base animation** — `fal-ai/kling-video/v2.6/pro/image-to-video`
   (`start_image_url` = the keyframe), driven by the Animation/Camera
   Instruction. Kling 2.6 (not 2.5) because 2.6 exposes `generate_audio`.
3. **Glitch + on-screen text** — local `ffmpeg` post, **free and
   deterministic**: `rgbashift`+`noise` bursts at chosen timestamps for
   the character's "thought leakage" beats, and a caption PNG (rendered
   with PIL, Georgia serif) overlaid via `overlay` with fades. **[manual]**
   - The AI video model must NOT be relied on for legible text or
     precise glitch timing — those belong in post.
4. **Ambient audio** — `fal-ai/mmaudio-v2` (video→audio), prompted for
   room tone / electronic hum / subtle glitch texture, negative-prompted
   against speech/music. Kling's own `generate_audio` produced a track
   but near-silent (~-42 dB) and speech-oriented; a dedicated audio model
   is the right tool. **[manual, not yet re-tested after a balance
   top-up]**
5. **Mux / final** — combine the above into the delivered clip; splice
   two 10s Kling clips if the 12s spec length is required (Kling caps at
   10s).

`SOMIA_VIDEO_PROVIDER=dry_run` (the default) still proves the code path
without any API key or cost. All fal.ai calls share the queue/upload
plumbing in `system/scripts/somia/fal_client.py`.

## Rejected approaches (do not repeat)

- **flux/schnell keyframe** — dropped the character entirely from
  multi-concept prompts. Rejected.
- **flux/dev keyframe (text-only)** — renders a clear subject but in a
  clean Western/"Disney-Pixar" register with no Japanese-illustration
  fetish appeal. Rejected for this brand.
- **Illustrious with prose prompts** — this checkpoint family needs
  Danbooru-style comma-separated tags; prose prompts came out rough/
  broken. Write Image Prompt (KV) as tags.
- **Illustrious text-only (no reference img2img)** — competent but
  "toy-like", low immersion, didn't hook. The reference-img2img base is
  what fixed it.
- **Pika 2.2 image-to-video** — repeatedly drifted a stylized keyframe
  toward photorealism mid-clip; `negative_prompt` did not reliably stop
  it. Rejected as default. (`providers_pika.py` kept only as a
  comparison record.)
- **Asking the video model for on-screen text / precise glitch / designed
  ambient audio** — unreliable. Moved to post (ffmpeg) and a dedicated
  audio model.
- **Horror-coded prompts** — empty corridors, "someone is already there",
  ominous captions read as horror when rendered, not intimacy. Every
  character stays in her own register but never dread. See
  `somia/BRAND/BRAND_IDENTITY.md`.

## Current code state vs the validated pipeline

`system/scripts/somia/render_content.py` + the provider adapters currently
implement only: text→image keyframe (Illustrious/flux/pika) → image-to-
video. They do **not** yet do reference img2img (stage 1), ffmpeg post
(stage 3), the mmaudio pass (stage 4), or muxing (stage 5). Those were run
as one-off scripts during testing. Wiring stages 1/3/4/5 into the
provider/pipeline code is the main follow-up.

Provider registry (`system/scripts/somia/providers.py`, vendor-agnostic
via `fal_client.py`):
- `illustrious_kling` — adopted default direction (Illustrious keyframe +
  Kling video).
- `kling`, `pika` — superseded; kept as comparison/architecture records.
- `dry_run` — no-cost path for testing the plumbing.

## Storage

- Generated media (keyframe*.png, video*.mp4) is git-ignored — it is
  reproducible from the specs and is large binary. Specs
  (`script.md`/`prompt.md`/`metadata.json`) are the source of truth.
- Reference KV images used for img2img should be kept as inputs, not
  treated as outputs.

## Control Rules

- Do not mix spec creation and content rendering.
- Do not skip reviewable artifacts.
- Do not hide source inputs.
