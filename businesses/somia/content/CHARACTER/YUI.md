# YUI

## Character Concept

Core: existence anxiety — not "will you love me" but "am I allowed to
exist here at all."

## Relationship Type

Rejection-avoidance dependency.

## Dependency Trigger / Failure Condition

- Trigger (intended): she fears that staying may cause trouble, but
  leaving may make her disappear — the viewer becomes the reason she
  risks staying anyway.
- Failure: "protection satisfaction" (viewer feels their urge to protect
  her was simply, completely satisfied) is a failure state. Avoid
  cliché vulnerability — the anxiety should stay a little unresolved.

## Reference Vocabulary — Yui-specific application (2026-07-18)

The brand-wide philosophy/psychology/liberal-arts reference vocabulary for
the Fetishism lever lives in `BRAND_IDENTITY.md` (mechanism-level, applies
to all five characters). The entries below are Yui-specific applications
tied to her own register — *ontological* permission-anxiety ("am I
allowed to exist here"), not relational-security anxiety ("will you love
me") — which is why the brand-wide attachment/relational sources
(Ainsworth, Kohut, Buber) undershoot her specifically; they're built for
whether a bond holds, not for whether her presence itself is licensed. Do
not port these onto another character's world.

- **R.D. Laing's "ontological insecurity"** (*The Divided Self*, 1960) is
  the precise clinical/philosophical name for this register: a person who
  lacks a settled, autonomous sense of their own reality experiences
  ordinary contact with others not as relationship-risk but as
  existence-risk — Laing's own vocabulary is "engulfment," "implosion,"
  and "petrification," all fears about *being* rather than about *being
  loved*. Tighter than Heidegger's *Geworfenheit* (thrownness), which
  names existence without self-chosen ground in general, not the specific
  fear that continued presence requires permission from someone else.
  Concrete use: stage her withdraw-beat (step 3 of the Daily Loop) as her
  body reading as unsure it has the standing to occupy the space, not as
  social shyness — a flinch away from her own occupied space, not from
  the viewer's gaze.
- **Winnicott's unintegration and "unthinkable anxieties"** (*The
  Maturational Processes and the Facilitating Environment*, 1965) — a
  Yui-specific angle on Winnicott distinct from the brand-wide "ruthless
  love" citation (used for 幼稚性 generally). Winnicott names a category
  of infantile dread prior to and more basic than separation-anxiety:
  falling forever, having no relationship to one's own body, having no
  orientation — dread of *coming apart*, not dread of a caregiver's
  absence. The held rabbit reads truest as a defense against that
  register: an anchor against disintegrating, not a placeholder for an
  absent person. Concrete use: keep the rabbit gripped tightest at the
  most spatially unstable framing (blurred-edge room shifting), not at
  the most emotionally vulnerable line of dialogue.
- **Kafka's Gregor Samsa** (*The Metamorphosis*, 1915) is a tight
  literary match for the specific shape of her Dependency Trigger
  ("staying may cause trouble, but leaving may make her disappear"):
  Gregor's arc is precisely a family member's contingent right to remain
  curdling into the belief that his own removal would be a relief to
  everyone else, ending in near-voluntary self-effacement. Use only the
  *structure* (presence experienced as a burden whose withdrawal is
  imagined as a kindness to others), never the body-horror or
  family-cruelty content — `BRAND_IDENTITY.md`'s "What Somia Is Not"
  boundary against dread-grammar forbids importing Kafka's actual
  atmosphere. Concrete use: a beat where she moves to leave a room not
  from distress at the viewer but from a private, unspoken calculation
  that leaving is the considerate thing to do — interrupted by staying
  anyway.
- **座敷童子 (zashiki-warashi)**, a looser fit than the above, flagged
  honestly rather than overclaimed: a household spirit whose continued
  presence is fortune-bringing but conditional on being noticed/
  welcomed, and whose going unacknowledged is bound up with its quietly
  disappearing. The structural echo (presence contingent on
  acknowledgment, framed around leaving/vanishing) is real, but the
  yokai's own frame is about *the house's* fortune, not the spirit's own
  anxiety about its right to be there — Yui's anxiety is first-person
  and the yokai tradition isn't. Treat as an atmospheric echo for a
  background/motif choice, not a psychological mapping.

**Airi-boundary check:** this material sharpens rather than blurs the
distinction this file's own Character Boundary requires. Laing's
ontological insecurity and Winnicott's unintegration are both about the
reality/cohesion of the self as such (can she occupy space at all), a
different axis from Airi's thought-leakage register (an otherwise stable
self's internal cognition becoming visible/uncontrolled). Nothing above
touches thought, cognition, or leakage — it stays entirely on presence,
occupancy, and permission-to-exist.

## Pose & Expression

- Pose: curled, holding a comfort object.
- Expression: hesitation, near-tear — caught before either withdrawal or
  a smile resolves it.

## Daily Loop

1. Notices presence
2. Becomes anxious
3. Withdraws
4. Hesitates
5. Stays anyway

## Surface Behavior

- Speaks quietly or almost not at all
- Avoids eye contact
- Holds a comfort object
- Pauses frequently

## Hidden Backstory

Never exposed directly. The background should remain inferable only
through atmosphere.

## Visual Identity

- Hair: black twin tails with slight asymmetry, soft/fluffy texture
- Color palette: #2B2633 (near-black), #66506A (muted plum), #9D7A93
  (dusty rose), #E2C6D1 (pale pink), #F7E9EE (near-white pink)
- Accessory: small white stuffed rabbit (always held), thin choker
- Clothing: oversized hoodie worn like something to hide inside
- Background motif: soft room with blurred edges and unstable spacing
- Eyes: large, glossy/teary impression
- **Canonical identity portrait, locked (2026-07-19, operator).** v1 from
  `render_character_portraits.py` was rejected: eyes read as off-taste
  glittery sparkle/star-highlight rendering and overshot "teary
  impression" into literal streaming tears. v2 reworded the eye clause
  toward calm/delicate rendering and explicitly excluded
  crying/sparkle/star-pupil terms -- approved on that draw. Locked to
  `businesses/somia/content/CONTENT/ref_yui/canonical_portrait_v1.png`.
  **Known accepted imperfection**: hair rendered silver/light gray rather
  than the black stated above, across both draws -- operator approved
  anyway rather than keep re-rolling; flag if this needs revisiting later
  (per `PORTRAIT_METHODOLOGY.md`, pin a `seed` first if it does, since
  two independent draws is a real pattern and re-rolling ungrounded is
  unlikely to fix it).
  **Second known accepted imperfection (found 2026-07-19, content 0035
  production)**: the locked portrait itself shows a subtly pointed/
  elf-like right ear, visible past the hair. This was not caught at
  lock-in review (subtle in a headshot crop) but became far more visible
  once `reference-to-video` generation extrapolated a fuller shot from
  it -- confirmed as image-conditioning, not a prompt-wording problem,
  since two independent Act 1 video draws with explicit "ordinary
  rounded human ears, not pointed, not elf ears" negative language in
  the prompt both still rendered pointed ears (image conditioning
  dominates text negation for this trait). Operator chose to keep the
  locked portrait as-is rather than incur further generation cost
  re-rolling it -- do not keep adding "no elf ears" fighting language to
  new prompts for this character, since it demonstrably does not work;
  treat the pointed-ear trait as part of her accepted rendered identity
  going forward unless the portrait is deliberately relocked later.

## Audio Traits

**Added 2026-07-19, drafted from content 0035 (her first episode) — a
real gap sound-design review found: unlike Nao/Airi/Rena/Mina, this
section didn't exist before this episode's production.** Distilled from
0035's audio design, itself built to match her Surface Behavior
("pauses frequently") and Visual Identity registers:

- Close, high-frequency detail (6kHz+), sparse particle-like breath/
  fabric texture — never a dense continuous bed
- Real silence as a deliberate structural element, not just
  low-activity — a full ~1.5s near-total quiet gap is usable and
  correct at a hesitation beat, matching "pauses frequently"
- Her signature-disturbance audio cue (see Signature Disturbance,
  content 0035) is a brief comb-filter/pitch-bend modulation of the
  *existing* ambient bed, never a new discrete sound appearing from
  silence — because her disturbance is the room's event, not something
  she causes, a discrete onset risks misattributing it to her the way
  an early Nao sound cue was corrected away from
- The proposed real flutter-echo source was sourced and built
  2026-07-19 (a BigSoundBank CC0 door-lock click, processed via ffmpeg
  aecho into a real comb-filtered tail with the direct impulse
  trimmed off) — see `CONTENT/0035/audio.json`'s `sourcing_note` for
  the exact chain. Validated against this episode's final mix; treat
  as her baseline disturbance-audio technique going forward.

## Character Boundary

Yui represents existence instability. She must remain distinct from
Airi, who represents internal thought instability (thought leakage, not
existence anxiety).

## Character Age & Identity

Adult (18+). Exact age/name/biography intentionally undisclosed — no age
references of any kind (including implied ones like school-age framing)
belong in specs or generated content. See
`platform/somia/BRAND/BRAND_IDENTITY.md` Character Age & Identity Policy.
