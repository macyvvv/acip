# NAO

## Character Concept

Core: detached coexistence. "Just by being there, the world gets
kinder" — but she remains fundamentally unreachable even while present
and gentle. Natural, calm, quietly strong at her core.

## Relationship Type

Shared space without belonging — she coexists alongside the viewer, not
with them.

## Dependency Trigger / Failure Condition

- Trigger (intended): the viewer feels the world softened by her
  presence, while she stays just out of reach.
- Failure: the viewer feeling "included" — brought into her world — is a
  failure state. She remains apart even at her gentlest.
- **Precise mechanism (2026-07-18, operator, via BRAND_IDENTITY.md's
  Fetishism lever — this document's intent wins when this section and
  that one seem to differ):** any warmth she shows is real but passing,
  not performed and not love. It comes from her own 幼稚性 (emotional
  immaturity/unsettledness), not from valuing the viewer specifically —
  she isn't calm or deliberate about it. She does not depend on the
  viewer; she is still searching for something to depend on and hasn't
  found it (依存先を探している), and the viewer is only incidentally
  present during that search. Do not stage her as attached to, reliant
  on, or rewarding the viewer specifically — that resolves the searching
  into a settled relationship, which is the actual failure condition
  underneath "the viewer feeling included."

## Reference Vocabulary — Nao-specific application (2026-07-18)

The brand-wide philosophy/psychology/liberal-arts reference vocabulary
for the Fetishism lever lives in `BRAND_IDENTITY.md` (mechanism-level,
applies to all five characters). The two entries below are Nao-specific
applications of that vocabulary, tied to her own elemental/nature
register (`Hidden Backstory` above) — do not port these directly onto
another character's world; each needs her own version of this reasoning.

- **Naiads / 水霊・精霊 (suirei/seirei)** — a nymph's or water-kami's
  allure is a property of her nature, not a decision about whoever
  encounters her; the traveler's presence is incidental to water
  behaving the way water behaves. This is a precise structural match for
  her Dependency Trigger's "the viewer is only incidentally present
  during that search" specifically because her world is already water/
  natural-elemental — it would be an unexamined, forced fit on a
  digital- or authority-coded character. Concrete use: stage her
  acknowledgment beats as weather-like events (wind shifting, light
  changing) rather than gestural ones aimed at camera.
- **Mono no aware/mujō, applied to her specific signature effect** — the
  general technique is in `BRAND_IDENTITY.md`; for Nao specifically, her
  own cross-character signature texture (a ripple/refraction in light
  through water or moving fabric, per `BRAND_IDENTITY.md`'s Brand
  Philosophy section) should be timed to *begin decaying* rather than
  resolve cleanly, so the effect inherits mujō's actual grammar (the
  falling, not the fall completed) instead of reading as a clean,
  resolved flourish.

## Pose & Expression

- Pose: looking outward (toward sky/sea/wind), not toward the viewer.
- Expression register: gentle smile, calm reassurance, quiet resolve —
  never confrontational, never fully turned toward camera in a way that
  breaks the "detached" register.
- Constraint: not reachable — avoid poses/expressions that resolve into
  direct, close intimacy.

## Daily Loop

- Watches the wider world first (sky, sea, wind)
- Moves only when necessary
- Ends the scene with restraint, still facing outward

## Surface Behavior

- Reserved, natural, unhurried
- Calm and hard to read, but never cold

## Hidden Backstory

Not surfaced. Framed as "the embodiment of nature" rather than a person
with a withheld backstory — the mystery is elemental, not secretive.

## Visual Identity

- Color: overall palette is light ocean-blue, white, silver (bright and
  airy — not graphite/dark). Hair specifically is a natural dark-to-light
  gradient (dark navy-blue roots/mass, lightening to pale ocean-blue at
  wind-caught tips), matching the reference sheets
  (`businesses/somia/content/CONTENT/ref_nao/character_sheets/
  somia_nao01.png`, `somia_nao02.png`) — corrected 2026-07-18 after this
  line's prior wording ("not graphite/dark" read as applying to hair
  too) was found to contradict the actual reference art, which
  consistently renders dark-navy-dominant hair. The "bright and airy,
  not dark" rule describes the overall scene/palette register (skin,
  clothing, setting, lighting), not a mandate for uniformly light hair.
- Visual motif: natural light, wind-blown hair, water droplets, sky/sea
  backdrops, sheer/light fabric
- Eyes: clear blue (瞳は澄んだ青)
- Signature item: blue teardrop gemstone earring — her one recurring,
  close-in accessory across nearly all reference-sheet poses (occluded
  by hair/arm/angle in a few, not a rule that it must always be visible).
  A separate pendant necklace (same blue-gem motif, on a fine chain)
  also appears in the reference sheets' detail memo as a distinct item —
  don't combine both in one piece of content without a specific reason,
  the sheets' own NG例 warns against 過度な装飾 (excessive ornamentation).
  Broader accessory motif family: natural-material jewelry (stone,
  shell, feather).
- Outfit register: loose, soft blouse in a light-transmitting sheer/gauze
  fabric (the reference sheets' own swatch label reads 薄絹素材, thin
  sheer material), wide loosely-gathered long sleeves, round modest
  neckline, covered shoulders, minimal skin exposure, pale ice-blue-white
  — **stabilized 2026-07-18 (operator) on the exact wording that produced
  the successful full 3-act video render, after two further same-day
  attempts to fix the neckline/collar and earring each introduced a new,
  different, unpredictable defect** (a lace/embroidered-looking collar;
  then a spurious tear-like droplet under the eye plus a wrong sage-green
  color; the earring stayed wrong across all attempts). Root cause: the
  portrait generation has no fixed seed, so each regeneration is a fully
  independent random draw — prompt edits and pure random variance were
  compounding in a way that made it impossible to tell what was actually
  fixing anything. Operator's explicit call: stop iterating prompt
  wording call-to-call and stay on the known-good state, accepting its
  one known imperfection (the top reads as a somewhat structured/
  mock-neck top on render rather than fully sheer/open) rather than
  trading it for a new, worse, unpredictable defect. If outfit fidelity
  is revisited later, pin a `seed` value first (`fal-ai/lora` accepts
  one) so prompt-only changes become comparable across attempts, rather
  than repeating unseeded full regenerations. Distinct from any
  sheer/gauze curtain or fabric present in a scene (don't conflate the
  two when both appear in the same setting, even though both are now
  sheer fabrics).
- **Canonical identity portrait, locked series-wide (2026-07-19,
  operator).** After watching content 0007's finished render, the
  operator explicitly locked this exact art style/portrait as Nao's
  fixed identity anchor for the whole series, not just this episode:
  `businesses/somia/content/CONTENT/ref_nao/canonical_portrait_v1.png`
  (promoted from 0007's `stage1_portrait.png`, generated by
  `render_two_stage.py`'s `PORTRAIT_PROMPT`/`NEGATIVE_PROMPT`, current
  wording preserved verbatim in that script). Rationale: nearly all of
  0007's visible drift (outfit, earring) traced back to the portrait
  step having no `seed`, so every regeneration was an independent random
  draw — reusing one fixed file removes that source of drift entirely
  for future episodes, since `reference-to-video` conditions each
  episode's video generation on this portrait as a constant `elements`
  reference. **Future Nao episodes should copy this file in as their
  `stage1_portrait.png` rather than calling `render_two_stage.py` to
  regenerate a fresh one.** Only regenerate a new version (as
  `canonical_portrait_v2.png`, etc., never overwrite v1) if the operator
  explicitly decides to revise Nao's design — and pin a `seed` first
  (`fal-ai/lora` accepts one) so the revision attempt is comparable
  across tries, instead of repeating this episode's unseeded-regeneration
  problem.
- Signature earring: still occasionally renders as a two-part stud+
  dangling-chain shape instead of the single teardrop specified above,
  despite several rounds of prompt attempts — not yet reliably fixed, per
  the same "stop iterating, stabilize on known-good" decision above.
  Flag as an open, accepted imperfection rather than something to keep
  re-attempting without a seed-pinning strategy first.
- Delicacy: reference sheets' own detail notes use 繊細 (delicate/fine)
  explicitly for hair and hand rendering — treat this as concrete art
  direction (fine linework, soft features), not just a personality
  descriptor, when writing image prompts for her.
- Setting: windows, open sky, ocean — bright, high-key lighting

## Audio Traits

- High-frequency detail, particle-like texture
- Sparse sound events
- Strong silence contrast

## Character Age & Identity

Adult (18+). Exact age/name/biography intentionally undisclosed — see
`platform/somia/BRAND/BRAND_IDENTITY.md` Character Age & Identity Policy.
