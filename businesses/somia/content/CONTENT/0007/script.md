# Script 0007 — "Window" (Nao, episode 1)

## Character

Nao

## Design Note (2026-07-18, fourth pass — full redesign after operator review of the 30s render)

History: v1 was a bare A/B-test stub with a palette contradicting
CHARACTER.md. v2 (10s single clip) fixed hair color, staged pacing,
added the cross-character VFX signature, softened on-screen text,
formalized `BRAND_IDENTITY.md`'s Brand Hierarchy. v3 (30s, 3 chained
Kling clips) fixed nothing new but exposed real defects the operator
caught directly:

1. **On-screen text was never composited into `video_30s.mp4`** — an
   execution miss (the compositing step used for v2 was not re-run for
   the chained version), not a design defect. Must be verified as
   actually present in the file before this counts as done, not assumed.
2. **Signature item never specified.** I (the orchestrator) had only
   read `CHARACTER.md`'s prose summary ("natural stone and shell
   jewelry") and never went back to the actual reference sheet images
   (`ref_nao/character_sheets/somia_nao01.png`, `somia_nao02.png`) before
   writing prompts. Re-reading those sheets directly: **a blue teardrop
   gemstone earring appears across most of the 20 pose/expression panels
   spanning both sheets** (corrected count, per epistemicsops — each
   sheet has 5 expression + 5 pose panels, not 10 total). It is not
   visible in every single panel: it is fully or partially occluded by
   hair/arm/angle in a few (sheet 1's poses D and E, sheet 2's expression
   05 and pose E). It is still her one consistent, recurring, close-in
   accessory motif — not one option among several — just not literally
   universal across every frame. This spec previously never named it
   explicitly enough for the model to render it reliably, and it did not
   read as a recognizable signature item in the actual output.
3. **Outfit drifted from the reference.** The reference sheets show a
   loose, long-sleeve, wide/off-shoulder-neckline sheer-knit top — not a
   tank top or camisole. This spec's `prompt.md` only described the
   window's sheer curtain in detail and never gave her own clothing an
   explicit description, so the model defaulted to a generic thin-strap
   top. Fixed below with an explicit clothing line separate from the
   curtain description.
4. **The single "one internal moment" beat became a repeated oscillation**
   in the 3-act chained render — profile, turn to camera, back to
   profile, turn to camera *again* near the loop point. The operator's
   words: this reads as 異変 (a malfunction/wrongness), not the intended
   違和感 (a single, deliberate, productive incongruity per
   `BRAND_IDENTITY.md`'s Brand Hierarchy) — and makes the overall
   situation unreadable rather than emotionally legible. Root cause:
   Act 3's prompt in v3 described "gaze lingering... before resolving,"
   language ambiguous enough that Kling generated a second fresh
   turn-and-smile instead of continuing an already-in-progress turn away.
   Fixed below with an explicit, unambiguous no-second-turn constraint on
   Act 3.
5. **Hair color: apparent CHARACTER.md-vs-reference-art contradiction,
   resolved as a gradient, not a pick-one-source decision.** color-
   coordination flagged that both reference sheets render Nao's hair
   predominantly dark navy at the roots/mass, lightening only at
   wind-caught tips — contradicting the v2/v3 prompt's blanket "not navy,
   not dark blue" language, which was written from `CHARACTER.md`'s prose
   ("light ocean-blue... bright and airy") without checking the actual
   reference art. Resolution: both sources are correct read as a natural
   dark-to-light gradient (dark navy roots, pale ocean-blue tips where
   light catches the wind-blown hair) rather than a uniform single tone
   in either direction — this matches the reference images' actual
   rendering and is consistent with `CHARACTER.md`'s intent (bright,
   airy *highlights*, not a mandate for flat uniform light color
   throughout). Also added: explicit blue eye color (瞳は澄んだ青,
   reference sheets' ディテールメモ), missing from every prior version's
   prompt.

**Process requirement for this pass** (per the operator): this redesign
must be reviewed by the full creative team (color-coordination,
lighting-design, sound-design, visual-effects, accessibility-review,
visualops, creativeops) plus epistemicsops, checked line-by-line against
`CHARACTER.md` and the actual reference sheet images for completeness and
consistency, with no open findings, *before* any new rendering is run.

## Signature Item (new section — was missing from prior passes)

**Blue teardrop gemstone earring/pendant** (from `somia_nao01.png`/
`somia_nao02.png`'s ディテールメモ close-up panel and present in all 10
pose/expression variations across both reference sheets). This is Nao's
equivalent of Yui's stuffed rabbit or Rena's wine glass — the one
recurring, close-in object that should read as recognizably *hers* across
every piece of her content, not just background-tagged jewelry. Every
act's image prompt must explicitly name it, and Act 2 (the one moment she
turns toward camera) should let it catch the light clearly — this is
also a natural, in-world place for a *second*, smaller instance of the
cross-character signature light-disturbance technique (a brief glint/
flare off the stone exactly as she turns), reinforcing rather than
competing with the water/curtain-light version already in the design.

## Outfit (new section — was previously undifferentiated from the curtain)

Loose, long-sleeve, wide/off-shoulder neckline sheer-knit top, pale
ice-blue-white, soft draped silhouette — per the reference sheets'
Image Key ("装飾品:天然石、薄絹素材" / sheer-fabric material) and every
pose variation shown. Explicitly NOT a tank top, camisole, or
thin-strap garment — this must be stated as its own prompt clause,
separate from the window curtain's own sheer-fabric description, since
conflating the two in v3's prompt is exactly what caused the drift.

## Timeline (~30s across 3 chained 10s clips)

### Act 1 — 0.0–10.0s: the hold (establishes immersion and situation clearly)

She is at the open window, profile to camera, gazing at sky and sea,
wearing the loose long-sleeve sheer-knit top (see Outfit above), the blue
teardrop earring visible at her ear. Sheer window curtain and her hair
move in the wind — two distinct fabrics, curtain and clothing, not
conflated. A slow, real held presence: a breath, a barely-there shift of
weight. This act's job is making the situation immediately legible (a
woman at a coastal window, present and calm) and immersive
(没入感) before anything emotional happens — no ambiguity about where
she is or what's happening. No on-screen text. No acknowledgment yet.

### Act 2 — 10.0–20.0s: the turn (the one internal-moment beat — happens exactly once)

Keyframed from Act 1's last frame; prompt re-asserts hair color, outfit,
and earring explicitly (guard against drift). A slight anticipation lag
before the head turn (gaze flicks first, head follows) at ~11-12s,
completing into the acknowledgment — small, incomplete smile — by
~14-15s. Hold the acknowledgment ~15-18s. Begin the turn back at ~18s,
**already meaningfully in motion by the end of this act** (not just
starting) — this matters for Act 3's continuity. She does not step
closer, does not extend a hand — stays framed by the window. At the turn
(~12-13s): (a) the light through the window curtain and off the sea
ripples/refracts, as if caught off guard with her, for a fraction of a
second, resolving back to stable light immediately after (the primary
cross-character signature beat, BRAND_IDENTITY.md); (b) a small,
secondary glint/flare catches the blue earring at the same moment —
reinforcing, not competing with, (a).

### Act 3 — 20.0–30.0s: the return and loop — NO second turn toward camera

Keyframed from Act 2's last frame (already mid-turn-away). **Explicit
constraint: she does not look at or turn toward the camera again at any
point in this act.** The turn-away motion that was already in progress at
the start of this act simply completes and settles — this is a
continuation, not a new beat, and must not be written or rendered as one.
Turn completes by ~23s into full profile. Wind settles by 27.0–30.0s. On-
screen text appears at 23.0–27.0s:
`So close. Still out of reach.`
**Must be verified present in the final composited file, not assumed.**
Final frame holds a pose visually close to Act 1's opening frame
(breathing/hair motion continues, not frozen) — the loop point. A 30s
clip that doesn't loop cleanly, or that ends on a second camera-facing
beat, defeats the entire rewatchability mechanic.

## Visual

Nao stays physically framed by the window throughout all three acts —
reachable in space, not reachable in address. She turns toward the viewer
**exactly once**, in Act 2, and the turn-away in Act 3 is that same
motion completing, not a second event. A full turn-and-approach, or a
second acknowledgment beat, would both be failure conditions per her own
CHARACTER.md (viewer feeling "included" is a failure state) and per
`BRAND_IDENTITY.md`'s distinction between productive 違和感 and
malfunction-reading 異変 — a repeated, unmotivated oscillation is the
latter, not the former.

## Audio

- Base: soft wind/sea ambient bed, held throughout all three acts
- Character noise: high-frequency detail, particle-like texture, sparse
  events (per Nao's Audio Traits)
- Action cue: a brief swell in the wind layer timed to the ~12s turn
  (Act 2), then a pull back to sparse/silent by ~27s (Act 3, strong
  silence contrast per her Audio Traits)
- Optional voice: none
- Standing gap (sound-design's mandate): no audio synthesis pipeline
  exists in this codebase yet — this spec, like all others, is unrealized
  in the actual deliverable. Not fixed by this pass.

## Text

`So close. Still out of reach.`
