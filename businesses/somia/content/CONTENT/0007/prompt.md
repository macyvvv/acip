# Prompt 0007 — "Window" (Nao, episode 1) — v5

## v5 change log (2026-07-18, after v4's keyframe generation broke)

v4's first real render produced a broken, flat/abstract/poster-like
keyframe — not a subtle art-direction miss, a technical failure. Root
cause: the keyframe step (Illustrious-XL via fal-ai/lora) needs short
comma-separated Danbooru-style tags, and its CLIP text encoder does not
understand grammatical negation. v4's prompt had become long descriptive
prose full of "NOT X" clauses in the *positive* prompt (e.g. "NOT a tank
top" inside the base description) — those tokens get embedded as
concepts regardless of the "NOT," and the long prose format itself
degrades this checkpoint's output (already documented in this repo's own
provider code comments). Fixed: every exclusion now lives only in the
negative prompt as a short tag; the positive prompt states only positive
facts, in short tags, not paragraphs.

Separately, the operator reviewed the corrected (but still off-shoulder)
keyframe and found two more real problems, addressed by re-reading both
reference sheets in full and transcribing them verbatim into
`businesses/somia/content/CONTENT/ref_nao/character_sheets/TRANSCRIPTION.md`
before touching this file again:

- **Outfit was wrong even after the "not a tank top" fix**: rendered as
  an off-shoulder top. The transcription's cross-check of every panel on
  both reference sheets found only incidental shoulder-adjacent drape in
  1-2 of 10+ panels, never a deliberate off-shoulder cut — the garment
  reads as a loose, soft, long-sleeved, high-necked cardigan-like top
  with minimal exposure across nearly every panel. Corrected below.
- **"Nao's delicacy was lost"**: the reference sheets' own detail notes
  use 繊細 (delicate/fine) explicitly to describe how her hair and hands
  are rendered — concrete art-direction language, not just an abstract
  personality trait. Added explicit delicate/fine-linework/soft-features
  tags that were never present in any prior version's prompt.

## Shared identity description (kept short deliberately -- see v5.1 note below)

delicate soft face, gentle blue eyes, soft eyebrows, delicate fine linework, long wind-blown hair, dark navy roots, pale blue tips, gradient hair, blue teardrop earring, soft cardigan, long sleeves, covered shoulders, high neckline, pale ice-blue top, ocean-blue white silver palette, high-key natural lighting, illustration, anime style

### v5.1 (same day): token-budget fix

The first v5 keyframe attempt combined the identity description above
with per-act scene/pose tags in one long prompt -- CLIP's effective
attention window is ~75 tokens, and the combined prompt exceeded it. The
later tokens (profile view, window/curtain/ocean scene) got diluted, and
the result was a close-up portrait against a flat background with no
scene at all, facing camera instead of profile -- not the outfit/
delicacy problem this pass was trying to fix, a new regression from
prompt length. Fixed: each act's own scene+pose tags now come FIRST in
that act's combined prompt, with the (now-shortened) identity description
appended after -- scene/pose changes per act and must survive if
anything gets truncated; identity tags are more forgiving of dilution
since they're reasserted identically in all three acts.

## Shared Negative Prompt (all three acts)

photorealistic, photo, 3d, western cartoon, disney, pixar, low quality, worst quality, bad anatomy, blurry, jpeg artifacts, nsfw, nudity, sexual content, revealing clothing, cleavage, exposed skin emphasis, bare shoulder, off shoulder, exposed collarbone, tank top, camisole, thin straps, sleeveless, revealing neckline, child, loli, school uniform, age indicators, direct eye contact, confrontational expression, flat colors, minimalist, abstract, poster art, silhouette, graphic design, solid color background, uniform single-tone hair, black hair, brown eyes, no earring, heavy makeup, sharp features, generic face, indoor artificial lighting, empty room, abandoned space, horror atmosphere, dark atmosphere, heavy decoration, flashy colors, excessive ornamentation, text, watermark, caption, logo, UI, letters, words, subtitles, border, frame, chart, diagram, sketch lines, monochrome, grid, collage, multiple panels

## Act 1 (0-10s) — Image Prompt (KV, keyframe generation)

1girl, solo, adult woman, standing at open window, window frame, sheer white curtain, ocean view, sky, sea background, wind, profile view, looking at sea, gentle calm expression, [shared identity description above]

### Act 1 Animation Instruction

A genuinely held presence establishing the situation clearly (a woman at a coastal window, present and calm) -- the full 10s spent on stillness: hair, curtain (separate from her clothing), and the cardigan's soft fabric all move continuously in the wind, a slow real breath, a barely-there weight shift. The blue teardrop earring stays visible and catches ambient light naturally throughout. She does not know/register the viewer during this act. No turn, no acknowledgment -- that begins in Act 2. Final frame of this act becomes Act 2's starting keyframe.

## Act 2 (10-20s) — keyframed from Act 1's last frame, image prompt reasserts identity to guard against drift

adult woman, [shared base description above], same pose as end of Act 1 (profile at window, gazing at sea) at the start of this act, gentle calm expression, blue teardrop earring prominent

### Act 2 Animation Instruction

Slight anticipation lag before the head turn (gaze flicks toward camera fractionally before head follows) beginning ~1-2s into this act, completing into a small, incomplete acknowledging smile by ~4-5s into this act -- per the reference sheets' own Pose C (sheet 2): "振り返る、一瞬こちらを見て微笑む" (turning back, glancing this way for a single instant with a smile) -- this beat is directly grounded in the source material, keep it brief and instant-like, not a lingering stare. Hold the acknowledgment for several seconds (~5-8s into this act). Begin the turn back at ~8s into this act, and this turn-back motion should be clearly, meaningfully underway (not just starting) by the very last frame of this clip. She does not step closer, does not extend a hand -- stays framed by the window, glass/threshold still between her and the viewer. **At the turn (~2-3s into this act), one coordinated light event with two facets, both brief and resolving immediately: (a) the light through the window curtain and off the sea ripples/refracts, as if caught off guard with her, for a fraction of a second -- a natural-world disturbance, NOT a digital glitch; (b) simultaneously, a small glint/flare catches the blue teardrop earring.** These are two facets of one event, not two stacked effects -- combined visual prominence should match the single-source intensity used for this same signature technique elsewhere (e.g. Airi's single glitch burst), not read as louder/more overt for being two-sourced. Both are subtle, in-world light behavior, not filters over the image.

## Act 3 (20-30s) — keyframed from Act 2's last frame (already mid-turn-away)

adult woman, [shared base description above], mid-turn continuing to return to profile at the window (already in motion, not starting a new pose), gaze and head still turning away from camera, settling expression, blue teardrop earring visible

### Act 3 Animation Instruction

**Hard constraint: she does not look at or turn toward the camera again at any point in this act, under any circumstance.** This act is the continuation and completion of the turn-away motion already in progress at the start of the clip -- not a new beat, not a fresh reaction, not a second acknowledgment. The turn completes into full profile by ~3s into this act. Gaze settles outward toward the sea, matching Act 1's opening register. Wind gradually settles through the remainder of the clip. Final frame should read as visually close to Act 1's opening frame -- same pose, same framing, in profile (not frontal), gaze directed at the sea (not at camera), blue earring visible -- the loop point. Do not introduce any new expression change, glance, or motion toward the viewer in this act. **Must be verified by extracting this final frame after rendering: confirm profile orientation and no eye contact with camera, not assumed from the prompt alone.**

## Camera Instruction (all three acts)

Static-to-subtle-push medium shot from just outside the window looking toward her profile; no cuts within or between acts' intended feel -- preserve a single continuous, unbroken-take quality across the full 30s even though it's technically three separate generations chained together.

## Model / Execution

illustrious_kling for Act 1's keyframe (Illustrious-XL v2.0 via fal-ai/lora) and Act 1's video (Kling v2.5-turbo/pro image-to-video). Acts 2 and 3 use Kling v2.5-turbo/pro image-to-video directly against the previous act's extracted last frame. `SOMIA_KLING_CFG_SCALE` at 0.4. Real fal.ai spend: 1 keyframe generation + 3 Kling video generations per attempt -- this is a third attempt after v3 (oscillation/missing text/wrong outfit) and v4 (broken keyframe from over-qualified prose prompt); verify the keyframe alone looks right before committing to the three video generations.

## Post-production (mandatory)

On-screen text ("So close. Still out of reach.", 23.0-27.0s) must be composited into the final chained/concatenated video using the `compositing-somia-onscreen-text` skill's method, and its presence verified by extracting a frame in that time window -- not assumed done because the step was run for a prior version.

## Not used in this episode (documented for future reference)

The reference sheets' detail memo shows a **separate pendant necklace**
(same blue-gem motif, worn on a fine chain, distinct from the earring)
and sheet 2's **Pose E** (sitting, hugging knees, quietly thinking — a
more private/vulnerable seated register than anything in this episode).
Neither is used here — adding both the earring AND the necklace risks
over-decorating a single 10s beat (the sheets' own NG例 warns against
過度な装飾/excessive ornamentation), and Pose E's seated register doesn't
fit this episode's window-standing blocking. Worth considering for a
future Nao episode, not retrofitted into this one.
