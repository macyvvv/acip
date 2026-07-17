# Prompt 0007 — "Window" (Nao, episode 1) — v4, redesigned after operator review

## Shared base description (reasserted in every act's own image prompt to guard against drift across chained generations)

adult woman, long wind-blown wet-look hair in a natural dark-to-light gradient (dark navy-blue roots and mass, gradually lightening to luminous pale ocean-blue at the wind-caught tips where light catches it -- a real gradient, not flat/uniform single-tone hair, not graphite-flat dark throughout), clear blue eyes, blue teardrop gemstone earring, loose long-sleeve wide off-shoulder-neckline draped ice-blue-white knit top (soft silhouette, matte-finish fabric, NOT a tank top, NOT a camisole, NOT thin-strap), standing at open window, translucent sheer white window curtain blowing in wind (visually distinct from her matte knit top -- curtain is see-through gauze, top is soft opaque knit), light ocean-blue white silver palette, high-key natural lighting, water droplets on hair, serene atmosphere, illustration, anime style, luminous natural light, cinematic medium shot, clean single-character illustration

## Shared Negative Prompt (all three acts)

photorealistic, photo, 3d, western cartoon, disney, pixar, low quality, worst quality, bad anatomy, blurry, jpeg artifacts, nsfw, nudity, sexual content, revealing clothing, cleavage, exposed skin emphasis, tank top, camisole, thin straps, sleeveless, child, loli, school uniform, age indicators, direct sustained eye contact from the start, confrontational expression, flat uniform hair color with no gradient, entirely graphite-dark hair with no light tips, entirely light-blue hair with no dark roots, black hair, brown eyes, no earring, missing earring, indoor artificial lighting, empty room, abandoned space, horror atmosphere, text, watermark, caption, logo, UI, letters, words, subtitles, border, frame, chart, diagram, sketch lines, monochrome, grid, collage, multiple panels

## Act 1 (0-10s) — Image Prompt (KV, keyframe generation)

1girl, solo, [shared base description above], looking outward toward sky and sea, profile view, gentle calm expression, quiet resolve, wind motion, coastal window setting clearly established, blue earring clearly visible at ear

### Act 1 Animation Instruction

A genuinely held presence establishing the situation clearly (a woman at a coastal window, present and calm) -- the full 10s spent on stillness: hair, curtain (separate from her clothing), and the sheer-knit top's fabric all move continuously in the wind, a slow real breath, a barely-there weight shift. The blue teardrop earring stays visible and catches ambient light naturally throughout. She does not know/register the viewer during this act. No turn, no acknowledgment -- that begins in Act 2. Final frame of this act becomes Act 2's starting keyframe.

## Act 2 (10-20s) — keyframed from Act 1's last frame, image prompt reasserts identity to guard against drift

adult woman, [shared base description above], same pose as end of Act 1 (profile at window, gazing at sea) at the start of this act, gentle calm expression, blue teardrop earring prominent

### Act 2 Animation Instruction

Slight anticipation lag before the head turn (gaze flicks toward camera fractionally before head follows) beginning ~1-2s into this act, completing into a small, incomplete acknowledging smile by ~4-5s into this act. Hold the acknowledgment for several seconds (~5-8s into this act). Begin the turn back at ~8s into this act, and this turn-back motion should be clearly, meaningfully underway (not just starting) by the very last frame of this clip -- Act 3 will treat that last frame as an in-progress turn-away, not a static acknowledgment pose. She does not step closer, does not extend a hand -- stays framed by the window, glass/threshold still between her and the viewer. **At the turn (~2-3s into this act), one coordinated light event with two facets, both brief and resolving immediately: (a) the light through the window curtain and off the sea ripples/refracts, as if caught off guard with her, for a fraction of a second -- a natural-world disturbance, NOT a digital glitch; (b) simultaneously, a small glint/flare catches the blue teardrop earring.** These are two facets of one event, not two stacked effects -- combined visual prominence should match the single-source intensity used for this same signature technique elsewhere (e.g. Airi's single glitch burst), not read as louder/more overt for being two-sourced. Both are subtle, in-world light behavior, not filters over the image.

## Act 3 (20-30s) — keyframed from Act 2's last frame (already mid-turn-away)

adult woman, [shared base description above], mid-turn continuing to return to profile at the window (already in motion, not starting a new pose), gaze and head still turning away from camera, settling expression, blue teardrop earring visible

### Act 3 Animation Instruction

**Hard constraint: she does not look at or turn toward the camera again at any point in this act, under any circumstance.** This act is the continuation and completion of the turn-away motion already in progress at the start of the clip -- not a new beat, not a fresh reaction, not a second acknowledgment. The turn completes into full profile by ~3s into this act. Gaze settles outward toward the sea, matching Act 1's opening register. Wind gradually settles through the remainder of the clip. Final frame should read as visually close to Act 1's opening frame -- same pose, same framing, in profile (not frontal), gaze directed at the sea (not at camera), blue earring visible -- the loop point. Do not introduce any new expression change, glance, or motion toward the viewer in this act. **Must be verified by extracting this final frame after rendering: confirm profile orientation and no eye contact with camera, not assumed from the prompt alone (v3's equally explicit-sounding Act 3 language still failed in practice).**

## Camera Instruction (all three acts)

Static-to-subtle-push medium shot from just outside the window looking toward her profile; no cuts within or between acts' intended feel -- preserve a single continuous, unbroken-take quality across the full 30s even though it's technically three separate generations chained together.

## Model / Execution

illustrious_kling for Act 1's keyframe (Illustrious-XL v2.0 via fal-ai/lora) and Act 1's video (Kling v2.5-turbo/pro image-to-video). Acts 2 and 3 use Kling v2.5-turbo/pro image-to-video directly against the previous act's extracted last frame. `SOMIA_KLING_CFG_SCALE` at 0.4 (per the v2 staged-prompt experiment). Real fal.ai spend: 1 keyframe generation + 3 Kling video generations -- this is a re-render of a previously-flawed attempt, not a first attempt; do not execute until the full-team review required by script.md's Design Note has completed with no open findings.

## Post-production (mandatory, was missed in v3)

On-screen text ("So close. Still out of reach.", 23.0-27.0s) must be composited into the final chained/concatenated video using the `compositing-somia-onscreen-text` skill's method, and its presence verified by extracting a frame in that time window -- not assumed done because the step was run for a prior version.
