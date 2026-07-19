# Airi LoRA Training Dataset — Generation Brief (for ChatGPT)

## Purpose

Generate a set of ~40–50 consistent training images of a single anime
character ("Airi") to be used for training a custom LoRA on the
Illustrious-XL SDXL checkpoint. The goal is to lock in the specific
traits that have proven fragile in prior generation attempts for this
character:

1. **Eyes and skin must NOT glow** — prior attempts describing the
   screen's light "reflected in her eyes" or "glowing" repeatedly got
   rendered as literal glowing eyes, a glowing aura, or glowing skin,
   pulling toward a fantasy-elemental look that is wrong for her. The
   light belongs to the environment around her, not to her body.
2. **Hair color** — black hair blended with deep purple mesh
   streaks running through it, fading to dark blue at the ends. Not a
   uniform pale light-blue wash, not a solid single color.
3. **Framing must include her shoulders/upper body and hairpin** — too-
   tight face crops have repeatedly excluded her signature hairpin and
   outfit entirely.
4. **No fantasy elements at all** — no glow, no ethereal/elemental
   imagery of any kind. She is a grounded, digital/screen-lit person,
   not a fantasy character.

## Character identity (fixed across every image)

- **Species/build**: adult woman, ordinary human, grounded and
  contemporary — not fantasy-coded in any way
- **Hair**: black hair blended with deep purple mesh streaks running
  through it, fading to dark blue at the ends, slightly messy tousled
  waves, minimal ornamentation
- **Hairpin (always present, always visible)**: one small angular
  metal hairpin — a cold-reading metal accessory, minimal, not
  decorative/ornate
- **Eyes**: deep, plain, unlit — NOT glowing, not sparkling; often
  unfocused, as if not fully present in the room; may show a pale-blue
  reflection cast ON them from an off-frame monitor, but the eyes
  themselves never emit light
- **Expression register**: ambiguous, unreadable — never a clear
  emotion. Pick one of: vaguely thinking (scattered focus), faintly
  anxious (brows barely knit), focused on a screen (attention fixed to
  one point), tired (heavy eyelids), noticing something (eyes waver for
  a moment). NEVER smiling, never crying, never a bright/cheerful
  expression.
- **Gaze**: avoid direct eye contact with the viewer; if present at
  all, must read as brief/incidental, never a sustained frontal stare
- **Outfit**: a loose, off-shoulder dark cut-and-sew top (thin knit,
  soft draping fabric) that slips down one shoulder. NOT a hoodie, NOT
  a tracksuit/zip-up jacket, NOT a thick sweater, NOT a choker.
- **Lighting on her**: pale-blue ambient light falls softly across one
  side of her face/body from an unseen off-frame source (a monitor) —
  the light is cast onto her from outside, it does not originate from
  her

## Art style (fixed across every image)

- Clean anime/manga illustration style, cel shading, delicate fine
  linework
- Explicitly AVOID: painterly rendering, watercolor texture, sketch/
  unfinished linework
- Setting mood: a night room, a cluttered-but-inhabited desk (mug,
  tablet, small plant nearby are fine as background props) — dim,
  screen-lit, slightly humid-feeling, never bright/high-key

## Reference material

If available, check the existing locked reference under
`ref_airi/canonical_portrait_v1.png` (or equivalent) and match its
established hair-color balance and framing.

## Required variety

Across the ~40–50 images, vary:

- **Angle**: front, 3/4 left, 3/4 right, side profile, slight above/
  below
- **Framing**: upper-body/bust and waist-up shots predominate — AVOID
  extreme close-ups/cropped-face-only shots, since those are exactly
  what previously excluded the hairpin and outfit; include a few full-
  figure or seated-at-desk shots too
- **Pose**: hugging her knees curled inward, collapsed forward onto a
  desk, hand at her chin (thinking), staring at a monitor, gazing out a
  window — vary these across the set, always a closed-off or inward-
  focused posture, never an open/performative one
- **Micro-expression**: rotate through the ambiguous expression list
  above — never repeat "clearly happy" or "clearly sad," keep every
  expression unresolved

## Do not cross-contaminate with other characters

This brief is one of five for a related character roster (Nao, Airi,
Rena, Mina, Yui). Airi's ONLY signature items are the small angular
metal hairpin and (background-only, not held/worn) a mug, tablet, or
small plant near her desk. **Do not include a stuffed rabbit, a blue
teardrop earring, a choker, a crescent hairpin, or a wine glass in any
image** — these belong to other characters in the roster, not Airi,
and including them will teach the LoRA a false association. If you are
reusing a template structure from another character's brief, remove
any panel/reference that introduces a prop not explicitly listed in
this document.

## What NOT to include

- No glowing eyes, glowing skin, glowing body, or any light-emitting
  effect originating from her
- No fantasy-elemental imagery, no ethereal aura, no sparkle effects
- No hoodie, no tracksuit/zip-up jacket, no thick sweater, no choker
- No legible on-screen text/UI in the background — screen content
  should read as texture only, never decodable words
- No bright smile, no sustained direct eye contact, no cheerful
  expression
- No extreme close-ups that crop out her shoulders/hairpin
- No other characters in frame, no watermarks/logos/captions

## Output format

Individual PNG files, portrait or square aspect ratio, high enough
resolution to downscale cleanly to 1024px. No captions/filenames needed
— captioning happens separately at the training step.

## Quick self-check before finalizing the set

For each image, confirm: eyes/skin are not glowing — hair reads black
with deep purple mesh fading to dark blue at the tips (not a uniform
pale wash) — hairpin visible — shoulders/upper body visible (not an
extreme close-up) — outfit is the off-shoulder dark knit top (not a
hoodie/sweater/choker) — expression is ambiguous, not clearly happy or
sad — clean anime linework (not painterly).
