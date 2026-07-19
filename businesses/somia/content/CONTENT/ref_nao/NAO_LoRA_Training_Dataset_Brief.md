# Nao LoRA Training Dataset — Generation Brief (for ChatGPT)

## Purpose

Generate a set of ~40–50 consistent training images of a single anime
character ("Nao") to be used for training a custom LoRA on the
Illustrious-XL SDXL checkpoint. The goal is to lock in the specific
traits that have proven fragile in prior generation attempts for this
character:

1. **Hair as a natural dark-to-light gradient** — dark navy-blue at the
   roots/mass, lightening to a pale ocean-blue at the wind-caught tips.
   Not uniformly light/pale, not uniformly dark.
2. **The signature earring as ONE continuous teardrop shape** — a
   single blue teardrop gemstone, hanging directly from its anchor
   point. It has repeatedly rendered as a two-part stud+dangling-chain
   shape instead — every image must show it as one unbroken teardrop.
3. **Outfit fidelity** — a loose, soft blouse in a light-transmitting
   sheer/gauze fabric, wide loosely-gathered long sleeves, a round
   modest neckline, covered shoulders. It has drifted toward reading as
   a more structured/mock-neck top than intended — emphasize the
   fabric's translucency and drape (how light passes through it, how it
   moves), not just the word "sheer."
4. **Clean anime cel-shaded illustration style**, delicate/fine
   linework — not painterly, not watercolor, not sketch.

## Character identity (fixed across every image)

- **Species/build**: adult woman, natural adult proportions, calm and
  quietly strong presence
- **Hair**: dark navy-blue at the roots, gradually lightening to pale
  ocean-blue at the tips, natural gradient (not a hard color-block
  transition), wind-blown/naturally tousled, delicate fine strand
  rendering
- **Eyes**: clear blue
- **Signature item (always present)**: one blue teardrop gemstone
  earring, rendered as a single continuous shape hanging from its
  anchor point — never a separate stud + chain + dangling stone
  arrangement. Include enough angles where the ear/earring is clearly
  visible.
- **Secondary accessory (occasional, don't combine with the earring in
  the same image without reason)**: a blue-gem pendant necklace on a
  fine chain — natural-material jewelry (stone, shell, feather) is her
  broader motif, kept sparse, never "excessive ornamentation" in one
  image
- **Outfit**: a loose, soft blouse in a light-transmitting sheer/gauze
  fabric, wide loosely-gathered long sleeves, round modest neckline,
  shoulders covered, pale ice-blue-white color — describe the fabric
  by how it behaves (translucent, light passing through, soft drape)
  rather than only naming it "sheer"
- **Color palette**: overall scene register is light ocean-blue, white,
  and silver — bright and airy, not graphite or dark (this applies to
  the palette/lighting/setting, not a mandate that the hair itself be
  uniformly light — see the hair gradient above)
- **Expression register**: gentle smile, calm reassurance, quiet
  resolve — never confrontational, never a fully direct, sustained
  frontal gaze at the viewer. Reserved, natural, unhurried. Calm and
  hard to read, but never cold.
- **Gaze**: usually looking outward (toward sky/sea/wind), not toward
  the viewer

## Art style (fixed across every image)

- Clean anime/manga illustration style, cel shading, delicate fine
  linework — a polished Japanese anime character portrait register
- Explicitly AVOID: painterly rendering, watercolor texture, sketch/
  unfinished linework, heavy/dark/graphite tonal rendering
- Bright, high-key, airy lighting — natural light, not moody or dim
- Simple, softly neutral backgrounds, OR light natural motifs (open
  sky, sea, window light, water droplets) consistent with her
  elemental/nature register — avoid busy/detailed man-made scenery

## Reference material

Existing locked references: `ref_nao/canonical_portrait_v1.png` and the
original character sheets `ref_nao/character_sheets/somia_nao01.png`,
`somia_nao02.png`. Match this established look, especially the hair
gradient and the earring shape.

## Required variety

Across the ~40–50 images, vary:

- **Angle**: front, 3/4 left, 3/4 right, side profile, slight above/
  below — enough angles that the earring is clearly visible in most
- **Framing**: close-up headshot, upper-body, waist-up, full figure —
  include several wider shots that show the blouse's sleeve/neckline
  construction clearly, not just close face crops
- **Pose**: looking out at the sky/sea/wind, seated, standing, a quiet
  resting pose — always calm, never an active/dramatic pose
- **Micro-expression**: gentle smile, quiet resolve, calm neutral,
  reflective — do not repeat the exact same expression throughout

## Do not cross-contaminate with other characters

This brief is one of five for a related character roster (Nao, Airi,
Rena, Mina, Yui). Nao's ONLY signature items are the blue teardrop
earring and (occasional, sparse) the matching pendant necklace /
natural-material jewelry motif described above. **Do not include a
stuffed rabbit, a hoodie, a choker, a crescent hairpin, a wine glass,
or a mug in any image** — these belong to other characters in the
roster, not Nao, and including them will teach the LoRA a false
association. If you are reusing a template structure from another
character's brief, remove any panel/reference that introduces a prop
not explicitly listed in this document.

## What NOT to include

- No other characters in frame; no text, watermarks, logos, or UI
- No exposed-skin emphasis beyond hands/face/collarbone as the outfit
  naturally allows; shoulders stay covered
- No two-part/segmented earring (stud + separate dangling chain) — the
  earring is always one continuous teardrop
- No mock-neck/structured, opaque-looking top — the blouse must read
  as soft, sheer, light-transmitting fabric
- No dark/graphite overall palette, no painterly/watercolor rendering,
  no sketch-style linework
- No fantasy/elf/demon markers, no school uniform, no chibi/child
  proportions

## Output format

Individual PNG files, portrait or square aspect ratio, high enough
resolution to downscale cleanly to 1024px. No captions/filenames needed
— captioning happens separately at the training step.

## Quick self-check before finalizing the set

For each image, confirm: hair gradient reads dark-navy-to-pale-blue
(not uniform) — earring is one continuous teardrop shape (not two-
part) — blouse reads sheer/translucent (not a structured mock-neck) —
clean anime linework (not painterly) — bright/airy palette — calm,
non-confrontational expression, not looking directly at the viewer in
most images.
