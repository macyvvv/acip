# Mina LoRA Training Dataset — Generation Brief (for ChatGPT)

## Purpose

Generate a set of ~40–50 consistent training images of a single anime
character ("Mina") to be used for training a custom LoRA on the
Illustrious-XL SDXL checkpoint. Mina's locked portrait was approved on
its first draw with no revision needed, so this brief has fewer known
failure modes to guard against than the other characters — the goal
here is mainly to lock in her established look consistently across a
larger, more varied set than the single portrait that's currently
canonical:

1. **Warm cream/amber/soft brown palette** — not violet, not cool-toned.
2. **A smile that is always incomplete** — never a full, resolved
   smile; always a small flicker/uncertainty in it.
3. **Soft, loosely-falling bun with escaped strands** — not a neat,
   fully-controlled hairstyle.
4. **Clean anime cel-shaded illustration style.**

## Character identity (fixed across every image)

- **Species/build**: adult woman, soft and warm presence
- **Hair**: a soft, loosely falling bun with escaped strands — a
  deliberate touch of undone-ness, not a tidy/perfect updo
- **Accessory (always present)**: a crescent-shaped hairpin
- **Expression register**: vacant/absent-minded (mental space
  elsewhere), a little lonely-looking, or a small, incomplete smile —
  NEVER a full/complete/broad smile, never an overly sweet expression,
  never a direct sustained stare at the viewer (if eye contact happens
  at all, it should read as brief/incidental)
- **Gaze**: often slightly down, or not directed at the viewer at all
- **Color palette**: warm cream, amber, soft brown — a lived-in, warm-
  light palette. NOT violet, not cool-toned.
- **Lighting**: warm-toned backlight or side light, enveloping rather
  than flat — never bright/harsh
- **Prop (recurring, near-constant)**: a simple, worn-looking mug,
  often held with both hands wrapped around it; steam rising from it
  reads as quiet motion when included
- **Setting mood**: a warm, domestic space (kitchen, soft-lit room),
  strong background blur is common

## Art style (fixed across every image)

- Clean anime/manga illustration style, cel shading — matching the
  rest of the cast's polished register
- Explicitly AVOID: painterly rendering, watercolor texture, sketch/
  unfinished linework
- Explicitly AVOID: bright/harsh lighting — always warm and enveloping

## Reference material

If available, check the existing locked reference under
`ref_mina/canonical_portrait_v1.png` and match its established look —
this was approved without revision, so it's a reliable single-image
anchor for hair, palette, and expression register.

## Required variety

Across the ~40–50 images, vary:

- **Angle**: front, 3/4 left, 3/4 right, side profile, slight above/
  below — enough angles that the crescent hairpin is clearly visible
  in most
- **Framing**: close-up headshot, upper-body, waist-up, full figure
- **Pose**: wrapping a mug with both hands, hand resting at her chin,
  body turned slightly to the side (a distance-making posture) — vary
  across the set, always calm/soft, never an active or dramatic pose
- **Micro-expression**: rotate through vacant/absent-minded, a little
  lonely-looking, and a small incomplete smile — never repeat a fully
  resolved happy expression

## Do not cross-contaminate with other characters

This brief is one of five for a related character roster (Nao, Airi,
Rena, Mina, Yui). Mina's ONLY signature items are the crescent hairpin
and the mug described above. **Do not include a stuffed rabbit, a blue
teardrop earring, a choker, or a wine glass in any image** — these
belong to other characters in the roster, not Mina, and including them
will teach the LoRA a false association. If you are reusing a template
structure from another character's brief, remove any panel/reference
that introduces a prop not explicitly listed in this document.

## What NOT to include

- No violet or cool-toned palette — always warm cream/amber/soft brown
- No fully complete/broad smile, no overly sweet expression
- No direct sustained eye contact with the viewer
- No bright/harsh/flat lighting — always warm and enveloping
- No neat, fully-controlled hairstyle — the bun should always have a
  few escaped strands
- No sketch/painterly rendering — always clean anime cel shading
- No other characters in frame, no watermarks/logos/captions, no
  fantasy/elf/demon markers, no chibi/child proportions

## Output format

Individual PNG files, portrait or square aspect ratio, high enough
resolution to downscale cleanly to 1024px. No captions/filenames needed
— captioning happens separately at the training step.

## Quick self-check before finalizing the set

For each image, confirm: palette is warm cream/amber/soft brown (not
violet/cool) — smile (if present) stays incomplete, never fully
resolved — hair is a soft loose bun with escaped strands (not neat) —
crescent hairpin visible — warm enveloping lighting (not bright/harsh)
— clean anime cel-shaded linework (not painterly).
