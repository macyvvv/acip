# Rena LoRA Training Dataset — Generation Brief (for ChatGPT)

## Purpose

Generate a set of ~40–50 consistent training images of a single anime
character ("Rena") to be used for training a custom LoRA on the
Illustrious-XL SDXL checkpoint. The goal is to lock in the specific
traits that took four revision rounds to converge on for this
character, and have proven fragile:

1. **Hair must be true black** — a prior attempt rendered it silver
   instead, despite the prompt asking for black.
2. **Outfit must read as luxury formal eveningwear, not tactical/
   combat gear** — describing the fabric as "matte black... light-
   absorbing" alone pulled a combat/tactical-harness aesthetic instead
   of the intended opulent register. Use explicit formal-eveningwear
   vocabulary (e.g. a black velvet gown), not just fabric-quality
   adjectives.
2b. **No garbled text-label artifacts** on clothing/accessories.
3. **Expression must stay cool/detached, never warm** — a prior
   attempt's smile read as too warm/friendly for her register. She
   should read as composed, unreadable, quietly superior — not smiling
   warmly.
4. **Clean anime cel-shaded illustration style** — a prior attempt
   drifted into a loose sketch/marker-style rendering, inconsistent
   with the rest of the cast's clean cel-shaded look.

## Character identity (fixed across every image)

- **Species/build**: adult woman, composed, elegant bearing
- **Hair**: true black, sleek and long, a matte-leaning straight
  texture (not glossy-wet-looking)
- **Eyes**: deep-set, minimal movement/expression — the eyes should
  read as measuring/observing rather than emotional
- **Expression register**: pick one of — expressionless (reflects
  nothing), an observing/measuring gaze, a faint unreadable smile
  (cool, not warm), a looking-down composition (quiet superiority), a
  moment just after a blink. NEVER a warm/friendly smile, never an
  overtly emotional expression, never seduction or aggression — quiet
  authority only.
- **Gaze**: she is never looked at first — gaze initiative always
  belongs to her; minimal eye/facial movement reads as controlled
- **Outfit**: matte black formal eveningwear (e.g. a black velvet
  gown), a light-absorbing fabric quality — luxury/opulent, not
  tactical, not a harness, not sporty
- **Accessory**: a choker is central to her design — sparse but
  meaningful decoration, not heavily ornamented
- **Color palette**: deep plum, black, wine red
- **Prop (recurring, optional)**: a wine glass — if included, stage it
  as something she is setting down or pausing over, not actively
  drinking from
- **Setting mood**: opulent, dim, controlled interiors — low-intensity
  spotlight lighting, never bright/flat

## Art style (fixed across every image)

- Clean anime/manga illustration style, cel shading, crisp linework —
  matching the rest of the cast's polished register
- Explicitly AVOID: loose sketch/marker-style rendering, painterly
  texture, watercolor texture, any garbled text/label artifacts
  anywhere on clothing or accessories
- Lighting: low-intensity, controlled spotlight — moody but clean, not
  murky/unclear

## Reference material

If available, check the existing locked reference under
`ref_rena/canonical_portrait_v1.png` and match its established look
(the fourth and final approved iteration).

## Required variety

Across the ~40–50 images, vary:

- **Angle**: front, 3/4 left, 3/4 right, side profile, slight above/
  below
- **Framing**: close-up headshot, upper-body, waist-up, full figure —
  include enough wider shots to show the gown's construction and the
  choker clearly
- **Pose**: elbow propped (controlling the moment with her gaze),
  leaning back showing composure, profile with gaze averted, holding a
  glass creating pause, a looking-down composition — always minimal
  movement, never a large/dramatic gesture
- **Micro-expression**: rotate through the expression list above —
  never repeat a warm smile or an overtly emotional look

## Do not cross-contaminate with other characters

This brief is one of five for a related character roster (Nao, Airi,
Rena, Mina, Yui). Rena's ONLY signature accessory is the choker
described above, plus the optional wine glass prop. **Do not include a
stuffed rabbit, a blue teardrop earring, a crescent hairpin, a mug, or
a hoodie in any image** — these belong to other characters in the
roster, not Rena, and including them will teach the LoRA a false
association. If you are reusing a template structure from another
character's brief, remove any panel/reference that introduces a prop
not explicitly listed in this document.

## What NOT to include

- No silver, gray, or light-colored hair — always true black
- No tactical/combat/harness-style clothing — always luxury formal
  eveningwear
- No garbled text or label artifacts on any surface
- No warm/friendly smile, no seduction, no aggression, no strong
  legible emotional expression
- No sketch/marker/painterly rendering — always clean anime cel
  shading
- No casual clothing, no excessive skin exposure, no large/energetic
  movement, no sentimentality
- No other characters in frame, no watermarks/logos/captions

## Output format

Individual PNG files, portrait or square aspect ratio, high enough
resolution to downscale cleanly to 1024px. No captions/filenames needed
— captioning happens separately at the training step.

## Quick self-check before finalizing the set

For each image, confirm: hair is true black (not silver/gray) —
outfit reads as luxury formal eveningwear (not tactical/combat) — no
garbled text artifacts anywhere — expression is cool/detached/
unreadable (not warm or smiling broadly) — clean anime cel-shaded
linework (not sketch/painterly) — deep plum/black/wine-red palette,
low-intensity controlled lighting.
