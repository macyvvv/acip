# Yui LoRA Training Dataset — Generation Brief (for ChatGPT)

## Purpose

Generate a set of ~40–50 consistent training images of a single anime
character ("Yui") to be used for training a custom LoRA on the
Illustrious-XL SDXL checkpoint (via Civitai's on-site trainer). The goal
of this dataset is to lock in four specific traits that have proven
very difficult to control through prompting alone on this checkpoint:

1. **Ordinary rounded human ears** — never pointed/elf ears
2. **True black hair** (not silver/gray)
3. **Twin-tails tied HIGH near the crown** — not low pigtails, not low
   braids, not drill-shaped curls
4. **Clean anime cel-shaded illustration style** — not painterly, not
   watercolor, not soft-blended/textured-canvas rendering

Every image in the set must be internally consistent on these four
points, since the LoRA will learn whatever the dataset actually shows,
including any accidental drift.

## Character identity (fixed across every image)

- **Species/build**: adult human woman, petite and slender, NOT a
  child, NOT chibi proportions
- **Ears**: ordinary rounded human ears, clearly visible in at least
  half the images (choose angles/hairstyles that don't fully hide them)
- **Hair**: true black (a very deep black, a faint blue-black sheen is
  fine), twin-tails tied HIGH near the top/crown of the head — think
  "high pigtails," not low braids or low pigtails — with slight
  asymmetry between the two tails, soft fluffy texture, not tight curls,
  not drill-shaped
- **Eyes**: large, soft, dark, a faint glossy sheen — calm and gentle,
  NOT sparkly/star-highlighted, NOT crying/streaming tears
- **Accessory (always present)**: one thin black choker
- **Signature item (always present)**: a small white stuffed rabbit
  plush, held close to her chest, one or both hands near it — vary the
  exact hand position across images but always keep the rabbit visibly
  present and intact (not dropped, not floating, not duplicated)
- **Outfit**: an oversized soft hoodie with long sleeves that cover her
  hands, a loose hood resting on her shoulders (hood down/relaxed, not
  covering her head, in most images so the hair/ears stay visible)
- **Color palette**: muted plum and dusty-rose accents against the
  black/charcoal hoodie and black hair — desaturated, soft, not bright
  or saturated
- **Expression register**: hesitant, withdrawn, caught between
  reluctance and a faint smile, gaze usually lowered or averted (not
  looking directly at the viewer in most images). Calm and quiet, never
  confident, smug, seductive, or "energetic." No hand gestures like
  peace signs, waving, or pointing — hands stay near the rabbit or
  resting quietly.

## Art style (fixed across every image)

- Clean anime/manga illustration style, cel shading, crisp delicate
  linework — the register of a polished Japanese anime character
  portrait (Illustrious-XL / Danbooru-tag-trained checkpoint aesthetic)
- Explicitly AVOID: painterly rendering, watercolor texture, oil-paint
  texture, visible canvas/paper texture in the background, loose sketch
  linework, unfinished line art
- Plain or very simple, softly neutral backgrounds — avoid detailed
  scenery, since the LoRA should learn the character, not a background

## Reference material

A prior concept sheet exists (attached separately /
`ref_yui/character_sheets/somia_yui03.png`) — use it for general mood,
palette, and proportions, but note it shows a lace camisole + open
cardigan rather than the hoodie described above. **Follow this brief's
hoodie description, not the camisole**, since the hoodie is what the
rest of the production (script, video-generation prompts) is already
built around. If useful, mention this discrepancy back to the operator
rather than silently picking one.

## Required variety (so the LoRA generalizes, not overfits)

Across the ~40–50 images, vary:

- **Angle**: front-facing, 3/4 left, 3/4 right, side profile, slight
  from-above, slight from-below — include enough front/3-4 angles that
  both ears are clearly visible in a good number of images
- **Framing**: close-up headshot, upper-body/portrait crop, waist-up,
  full standing/sitting pose — do NOT make every image an extreme
  close-up; several images must show the full twin-tail length and
  height clearly
- **Pose**: sitting curled up, standing, kneeling, leaning against
  something — always holding or near the rabbit, never an active/
  energetic pose
- **Micro-expression**: the full range within her register (quiet
  neutral, faint uncertain smile, slightly worried, softly looking
  down, softly looking away) — do not repeat the exact same expression
  in every image

## Do not cross-contaminate with other characters

This brief is one of five for a related character roster (Nao, Airi,
Rena, Mina, Yui). Yui's ONLY signature items are the black choker and
the small white stuffed rabbit plush described above. **Do not include
a blue teardrop earring, a crescent hairpin, a wine glass, or a mug in
any image** — these belong to other characters in the roster, not Yui,
and including them will teach the LoRA a false association. (Confirmed
necessary: an actual Nao dataset draft accidentally included a "Rabbit
Reference" panel copied over from this brief's template — check any
reused template structure for stray panels like this before finalizing
a set for a different character.)

## What NOT to include

- No other characters in frame
- No text, watermarks, logos, or UI elements
- No sexualized framing, no exposed-skin emphasis beyond hands/face
- No school uniform, no fantasy/elf/demon markers of any kind
- No jewelry or accessories beyond the choker (keep the "signature
  item" reading as the rabbit alone)
- No pointed ears, no silver/gray/white hair, no low pigtails/braids,
  no drill-curled twin-tails, no painterly/watercolor rendering — these
  five are the exact defects this dataset exists to correct, so they
  must not appear anywhere in the set

## Output format

- Individual image files (PNG preferred), roughly square or portrait
  aspect ratio, high enough resolution to downscale cleanly to 1024px
  (Illustrious-XL's native training resolution)
- No captions/filenames needed from ChatGPT — captioning will happen
  separately during the Civitai training step

## Quick self-check before finalizing the set

For each image, confirm: black hair (not silver/gray) — ears rounded
and human where visible (not pointed) — twin-tails tied high (not low)
— clean anime linework (not painterly) — rabbit present and intact —
choker present — hoodie present — expression within the hesitant/quiet
register (not confident/smug/gesturing).
