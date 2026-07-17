# Script 0007 — "Window" (Nao, episode 1)

## Character

Nao

## Design Note (2026-07-18 rewrite, revised same day after 6-role review)

The prior version of this file was a bare A/B-test stub (`variation_type:
silence_duration`) with a keyframe prompt using a graphite/dark palette
that contradicted Nao's own CHARACTER.md visual identity (light ocean-blue
/ white / silver, bright and airy — not graphite). Rewritten as a complete
scenario, built specifically for repeat viewing per BRAND_IDENTITY.md's
core concept (relational fetishism + emotional dependency, not horror —
no empty/abandoned space, no implied-unseen-threat grammar). The loop
point at the end is a deliberate rewatchability mechanic: the final frame
returns close to the opening frame/pose so the clip reads as a seamless
loop on autoplay.

Second pass, after a full review of the rendered `video_final.mp4` by
color-coordination, lighting-design, sound-design, visual-effects,
accessibility-review, visualops, and the operator:
- Hair color fixed: `prompt.md`'s own KV prompt literally said "dark blue
  hair" (a specific-token-overrides-general-palette-phrase bug,
  visualops's finding) — corrected to pale/light ocean-blue with explicit
  negative-prompt reinforcement.
- On-screen text softened from "Close, but never quite here." to "So
  close. Still out of reach." — lighting-design flagged the original as
  borderline the BRAND_IDENTITY.md-prohibited "ominous text" pattern;
  same meaning, warmer/more wistful register.
- Timeline restructured into three explicit held beats (was a single
  continuous drift) to address the "mechanical, no held beats" critique
  — see `prompt.md`'s Animation Instruction for the beat-by-beat design.
- Added the cross-character signature technique (`BRAND_IDENTITY.md`,
  added same day): a brief visual-noise disturbance at her one internal
  beat, native to her elemental/natural world (water/light refraction,
  not a digital glitch — that texture is Airi's world only and would
  read as horror-coded intrusion in Nao's). visual-effects had
  originally (incorrectly) scored Nao as not needing this technique at
  all; corrected once the operator clarified it's a brand-wide signature
  at consistent strength, character-native texture.

## Timeline (10s, Kling duration cap — 3 explicit beats, not continuous drift)

- 0.0–4.0s (beat 1, held): Medium shot, Nao at an open window, back/profile
  to camera, gazing out at sky and sea. Sheer curtain and her hair move in
  the wind. She is fully present in her own world — not reaching toward
  the viewer. This beat is deliberately longer than the original 2.5s cut
  so it reads as genuinely held, not transitional.
- 4.0–7.0s (beat 2, the turn): A slight anticipation lag before the head
  turn (gaze flicks first, head follows) — the one acknowledgment beat
  required by BRAND_IDENTITY.md's "an expression that acknowledges the
  viewer" rule. Small, incomplete smile. She does not step closer, does
  not extend a hand — she stays framed by the window, the glass/threshold
  still between her and the viewer. At the exact moment of the turn, the
  light through the curtain and off the sea ripples/refracts, as if
  caught off guard with her, for a fraction of a second — the
  cross-character signature "internal moment" noise, rendered as a
  natural-world disturbance in the light itself rather than a digital
  effect — then resolves back to stable light immediately after.
- 7.0–10.0s (beat 3, the return): The turn back is slower than the turn
  in, gaze lingering half a second after the head has already started
  rotating back, before the smile fully resolves into anything closer or
  more intimate. On-screen text appears at 7.0–9.0s:
  `So close. Still out of reach.`
  Wind settles by 9.0–10.0s; she holds a pose visually close to the
  opening frame (breathing/hair motion continues, not a frozen still) —
  the loop point.

## Visual

Nao stays physically framed by the window throughout — she is reachable
in space (the viewer can see all of her) but not reachable in address
(she only turns toward the viewer once, briefly, and turns back). The
"almost, not quite" quality is the whole point; a full turn-and-approach
would be the failure condition per her own CHARACTER.md (viewer feeling
"included" is a failure state).

## Audio

- Base: soft wind/sea ambient bed
- Character noise: high-frequency detail, particle-like texture, sparse
  events (per Nao's Audio Traits)
- Action cue: a brief swell in the wind layer timed to the 5.0s turn,
  then a pull back to sparse/silent by 9.0s (strong silence contrast,
  per her Audio Traits)
- Optional voice: none

## Text

`So close. Still out of reach.`
