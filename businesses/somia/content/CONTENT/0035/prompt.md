# Prompt 0035 — "Stays Anyway" (Yui, episode 1)

## Revision note (2026-07-19, after full multi-lens review)

**Second revision (2026-07-19, after first full-chain regeneration):** filmmaker's finding that the push-in over-executed within Act 3 (drifting from wide/medium-full to a tight face close-up, breaking the loop-closure comparison against Act 1's opening) was fixed with explicit per-act frame-scale hard limits in Act 3, a legibility requirement on Act 4's ease-back, and a framing-match requirement on the bridge's endpoints. The regeneration this fix triggered introduced a new defect on its own: Act 4 rendered a resolved, pleased smile and drifted the furniture from the established floor-cushion nook to a couch with throw pillows -- both fixed with explicit no-smile/unresolved-expression and same-furniture language added to Act 4's prompt below.

Applied: hoodie construction language restored to the fuller phrasing
that actually converged on the locked portrait (apparel-stylist); the
shared identity block's rabbit clause made generic so it no longer
contradicts Act 2's own "held one-armed" staging in the same generation
call (apparel-stylist); Act 3 given an explicit rabbit-stability clause
so the geometry disturbance doesn't bleed onto the rabbit (apparel-
stylist); the Signature Disturbance resolved to one named technique
(double-exposure ghosting, quantified) plus a no-startle guard and
horror-adjacent negative-prompt exclusions (visual-effects); Act 3's
Kafka-structure motivation given an implied (unnamed) beneficiary
instead of "no one" (philosophy-review); Act 1 given an external audio
trigger and Act 2's hold given an internal micro-event (character-
psychology, philosophy-review, liberal-arts-review); the Act 3→4 camera
boundary closed (filmmaker); the bridge's target changed from Act 1's
literal first frame to a near-opening frame, and given an explicit
rabbit-grip closing clause (filmmaker, character-psychology); a
foreground blanket-edge element added for visual variety across the
full runtime (filmmaker). See `script.md`'s Review Pass section for the
full reasoning behind each change.

## Shared identity description (short, tag-form — per the lesson from
Nao's v5.1 token-budget defect: scene/pose tags come first per-act,
identity description appended after, kept short enough to survive
truncation)

1girl, solo, adult woman, silver-gray hair, soft asymmetric twin tails, fluffy hair texture, large glossy eyes, restrained teary impression, not crying, no tear streaks, no sparkle highlights, thin choker, oversized soft hoodie, thick fabric loosely swallowing her hands at the sleeve cuffs, hood resting loosely at her shoulders, small white stuffed rabbit, one continuous soft plush shape with no separate floating parts, muted plum and dusty rose and pale pink palette, near-black shadow tones, soft blurred-edge room background, uneven room proportions, loose blanket edge visible near-frame at lower edge, dim quiet lighting, illustration, anime style

## Shared Negative Prompt (all acts + bridge)

photorealistic, photo, 3d render, western cartoon, disney, pixar, low quality, worst quality, bad anatomy, blurry, jpeg artifacts, watermark, signature, text, caption, subtitles, black hair, brown hair, no rabbit, rabbit absent, dropped rabbit, floating rabbit parts, duplicated rabbit, sustained direct eye contact, camera-facing gaze, gaze at viewer, resolved full smile, open-mouth grin, visible teeth, exposed skin, cleavage, midriff, swimsuit, sexual content, school uniform, backpack, child body proportions, chibi, loli, age indicators, horror atmosphere, dark atmosphere, jump-scare framing, startled expression, wide-eyed shock, symmetrical composition, screen glow, monitor, glitch effect, chromatic aberration, water ripple effect, warped architecture, impossible geometry, backrooms, liminal space, uncanny, surreal distortion, dutch angle

## Act 1 (0-9s) — Image Prompt (KV, keyframe generation)

curled on floor cushion, corner of room, knees drawn in, blanket around legs, rabbit held to chest with both arms, chin low, gaze downward, still posture, quiet breath, fixed static camera, slightly off-center medium-close framing, low seated-eye-level, [shared identity description above]

### Act 1 Animation Instruction

Held presence for ~3s (breath, minute weight shift, not a locked frame), then at ~3.0-4.5s her head lifts a small controlled degree and her gaze drifts toward the middle distance of the room only -- never toward the camera, no gaze-lock at any point in this act or any other. This moment is paired with a single near-imperceptible breath-catch in the ambient audio (see audio.json) -- an external, non-visual trigger for the notice, since she never looks toward camera to confirm it herself. No startle, no gasp, no widened eyes. From ~5.0s her grip on the rabbit tightens incrementally in one direction only, no loosening, through to the act's end. Camera: single continuous barely-perceptible constant-rate push-in starts from frame 1, no reversal, no re-acceleration. Final frame: gaze at middle distance, visibly tighter grip than the opening frame, same curled posture otherwise. This final frame becomes Act 2's starting keyframe.

## Act 2 (9-18s) — keyframed from Act 1's last frame, reasserts identity to guard against drift

silver-gray hair, twin tails, oversized soft hoodie, hand moving to raise hood, hood half-raised, shoulders drawn inward, weight angled into corner, rabbit held one-armed against her side, camera continuing the same slow push-in rate as Act 1, [shared identity description above]

### Act 2 Animation Instruction

Grip-tightening from Act 1 continues ~1-2s then resolves into a contained shoulder-inward flinch (small, not dramatic) and a fractional weight shift deeper into the corner. One hand releases the rabbit partway and moves to draw the hood up; this lift motion stalls at the halfway point by ~14.5s and holds there for the remainder of the act -- one continuous single-direction arc (lift, then stall, then hold), it must not restart, reverse, or repeat. The hold is not empty duration: her breath continues visibly against the stalled hand, and a faint, separate secondary grip-adjustment on the rabbit's arm (distinct from Act 1's already-resolved tightening, a small additional increment, not a repeat) occurs partway through the hold. Camera: push-in continues at the same constant rate established in Act 1, no change in rate or direction. On-screen text 15.0-17.5s: "I didn't move." Final frame: hood half-raised, hand resting at the stalled point, shoulders still drawn in. Becomes Act 3's starting keyframe.

## Act 3 (18-28s) — keyframed from Act 2's last frame (hood mid-stall)

silver-gray hair, hand releasing the stalled hood motion, weight shifting forward and up, one hand pressed flat on cushion, body angled a few degrees toward unseen doorway, rabbit gripped tightly but rendered as one stable solid plush shape, cushion-nook edge showing a brief double-exposure ghost line, camera continuing the same slow push-in rate but the frame must still clearly show her knees, the cushion edge, and both hands with the rabbit -- wide/medium-full framing maintained throughout, not a close-up, [shared identity description above]

### Act 3 Animation Instruction

First ~1s resolves the prior hood-stall cleanly (lowers or stays, non-load-bearing). At ~20.0-23.0s a genuine partial rise: one hand presses flat on the cushion, weight shifts up and forward by a real but small amount, body angles a few degrees toward the room's unseen doorway -- motivated as a private, unspoken calculation that leaving would be the more considerate thing (for whoever else might need the space -- diffuse and unnamed, never addressed to camera, but not a kindness to no one at all), never as distress at being watched. At ~23.0s the disturbance ARRESTS this rise -- it is the cause, not a coincidence: the nearest visible edge of the cushion-nook (or nearest wall line if that edge is out of frame) briefly renders as two near-identical overlapping lines, offset laterally by roughly 3-5% of frame width, both simultaneously visible for approximately 4-6 frames at 24fps (under a quarter second), then the ghost line fades back into the primary line, returning to a single clean edge -- a brief duplicate-then-merge, not a gradual drift, not a digital glitch, not a light/water ripple. The rabbit itself stays a single stable, solid white plush shape throughout this moment, completely unaffected by the geometry disturbance -- the disturbance is confined to the room's architecture only, never to her or the rabbit. Her grip on the rabbit reaches its single tightest point of the whole piece at this exact moment, caused by witnessing the disturbance, not by the on-screen text. No startle, no widened eyes, no reactive flinch toward the disturbance -- her only visible response is the grip. The partial rise does not complete or reverse further after this point; weight stays arrested, partly forward, for the rest of the act. **Camera scale hard limit (added 2026-07-19 after filmmaker found the push-in over-executing within this act): the accumulated push-in across Acts 1-3 must stay small -- by this act's end the frame must still clearly show her knees, the cushion edge, and both hands holding the rabbit. It must NOT tighten into a face-only or upper-chest-only close-up; if in doubt, keep the shot wider rather than tighter.** On-screen text 24.5-27.0s: "Maybe it's fine. Maybe." Final frame: weight still arrested mid-rise, tightest rabbit grip, room geometry already resolved back to baseline (the ghost line is gone by this frame), framing still wide/medium-full with knees and cushion edge visible. Becomes Act 4's starting keyframe.

## Act 4 (28-37s) — keyframed from Act 3's last frame (weight arrested mid-rise)

silver-gray hair, weight lowering back onto cushion, settling posture, blanket resettling around legs, hood lowering partway, rabbit grip loosening toward chest-held position, chin lowering toward rabbit, gaze low, no smile, neutral or faintly worried mouth, expression stays unresolved and uncertain, same floor cushion nook and room corner as every prior act (not a couch, not a sofa, no throw pillows), camera continuing the push-in for the first ~2s then easing back, [shared identity description above]

### Act 4 Animation Instruction

For the first ~2s (28.0-30.0s), camera continues the exact same push-in rate carried over from Acts 1-3 -- no pause, no held position, no ambiguity about what the camera is doing in this window. Arrested rise does not complete upward -- over ~1-3s weight lowers back onto the cushion in one continuous downward arc, no false starts, no smile forming at any point. At ~30.0s, and not before, the camera's only direction change in the whole piece begins: a single slow ease-back at roughly the push-in's own rate, reversed -- staged as the settling motion continuing, not as resolving or releasing anything. **This ease-back must be clearly legible on screen, not a subtle/imperceptible correction (added 2026-07-19 after filmmaker found the prior draw's ease-back invisible): by the act's end the framing must have visibly loosened back to a wide/medium-full scale closely matching Act 1's opening shot, with her knees, the cushion edge, and her full curled posture again clearly in frame.** By ~31-33s blanket resettles, hood (if raised) lowers partway from the settling motion itself, not a separate deliberate gesture; rabbit grip loosens from Act 3's peak back toward (not past) its Act 1 opening level, one continuous loosening arc. By ~34s posture should closely match Act 1's opening frame: curled on the same cushion, rabbit held to chest with both arms, chin lowering toward it, gaze low, same wide/medium-full framing as Act 1's opening -- close, not identical; a small, deliberate residual difference in exact grip/posture is fine and expected, the loop is approached, not landed on exactly. On-screen text: "I didn't disappear." at 33.0-35.0s, then "Not this time." at 35.5-37.0s, with a real gap between the two lines, not one continuous sentence. Final frame: the loop-target posture, wide/medium-full framing, breath still visibly present, not frozen. This final frame is the bridge's start_image_url.

## Bridge (37-41s) — image-to-video interpolation

`fal-ai/kling-video/o1/image-to-video`, `start_image_url` = Act 4's extracted last frame, `end_image_url` = a frame extracted from early in Act 1 (NOT Act 1's literal first frame -- a beat into the act, close to but not identical to the true opening frame, so the loop is implied by extreme closeness rather than completed by an exact return). **Framing requirement (added 2026-07-19 after filmmaker found the prior draw's bridge collapsing to a tight face close-up that no longer matched Act 1's shot scale): both endpoint frames must be the wide/medium-full framing established in Act 1 -- her knees, the cushion edge, and her full curled posture visible in frame. If Act 4's actual last frame is not wide/medium-full framing, do not feed it into this bridge; regenerate Act 4 first.** Content: blanket settles a fraction further, breath continues at a slow even rate, her grip on the rabbit settles its final small remaining amount toward Act 1's opening looseness (closing the residual hand/rabbit differential between the two endpoint images explicitly, rather than leaving the model to invent that motion unguided), and room edges make one final small, gentle re-settle toward the Act 1 opening configuration -- calmer and smaller than the Act 3 double-exposure ghost, not a repeat of that event. No on-screen text. No additional camera direction beyond what the interpolation itself introduces.

## Model / Execution (proposed, mirrors Nao's 0007 validated method)

Stage 1: reuse `ref_yui/canonical_portrait_v1.png` directly as the constant identity element (already locked and known-good, avoiding an unseeded-regeneration drift risk analogous to the one Nao's episode hit before her portrait was locked). Acts 2-4: `fal-ai/kling-video/o1/reference-to-video`, conditioned on the locked portrait as a constant identity element plus each act's own extracted last frame as the start-frame reference, same chaining method as `render_final_3act.py`. Bridge: `fal-ai/kling-video/o1/image-to-video` per above. `extract_last_frame()`'s sharpest-of-several-candidate-frames method (added for Nao after a motion-blur defect) should be reused here rather than grabbing the literal last frame. Per apparel-stylist's iteration-discipline note: no seed is pinned for these calls; if any further wording comparison is wanted before generation, pin a seed first rather than judging unseeded before/after draws against each other.

## Post-production (mandatory, per Nao's confirmed miss)

On-screen text must be verified as actually composited into the final assembled video by extracting a frame in each stated text window, not assumed done because the step ran for a prior version. Final assembly should re-encode into one continuous stream (concat filter, not `-c copy` concat demuxer) per Nao's confirmed playback-freeze bug at act boundaries.
