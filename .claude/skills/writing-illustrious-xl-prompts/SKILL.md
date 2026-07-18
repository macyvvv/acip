---
name: writing-illustrious-xl-prompts
description: Rules for writing positive/negative prompts for Illustrious-XL v2.0 (and other Danbooru-tag-trained SDXL/CLIP-family checkpoints) via fal-ai/lora, discovered the hard way across somia content 0007 (Nao episode) after a "NOT X in the positive prompt" mistake broke a keyframe generation, and four further attempts each lost a different required element to token-budget dilution. Use this before writing or reviewing any image-generation prompt for this checkpoint family -- especially when a single prompt must carry both character identity and scene/pose.
---

# Writing prompts for Illustrious-XL / Danbooru-tag SDXL checkpoints

## Rule 1: exclusions go only in the negative prompt, never as "NOT X" in the positive

CLIP text encoders (the ones these checkpoints use) do not parse
grammatical negation. Writing "NOT a tank top" or "NOT off-shoulder" inside
the *positive* prompt tends to reinforce "tank top" / "off-shoulder" as a
concept to include, not exclude -- the negation word itself carries little
to no weight in the embedding.

- Every concept you want absent from the image goes in `negative_prompt`
  as a short tag (e.g. `off shoulder, tank top, bare shoulder`).
- The positive prompt states only what should be present, as positive
  facts. Never write a negation clause in it, however natural it reads in
  English.
- Confirmed failure mode: content 0007's v4 keyframe broke outright (flat,
  poster-like, unusable) after the positive prompt accumulated several
  "NOT X" clauses combined with long descriptive prose.

## Rule 2: short comma-separated tags, not prose

This checkpoint family is trained on Danbooru-style short tags. Long
descriptive sentences degrade output quality even when they contain no
negation at all. Keep both positive and negative prompts as short,
comma-separated tag lists.

## Rule 3: the effective prompt-attention budget is roughly 75 tokens

Past that point, later tokens get diluted or dropped -- there is no
reliable ordering trick that preserves everything once you're over budget.
This is a real architectural limit, not a wording problem.

Confirmed empirically across four consecutive single-stage attempts on
content 0007, each combining full identity (face, hair, earring, outfit,
delicacy) with a scene description in one prompt -- each attempt sacrificed
a *different* element:
1. Scene-first ordering: lost the outfit (reverted to off-shoulder).
2. Identity-first, scene tags appended: scene got diluted, portrait came
   out as a close-up with no window/curtain/sea at all.
3. Ruthless trimming to only "load-bearing" tags: lost face/earring
   visibility (obscured by hair, awkward composition).
4. Further trimming attempts kept trading one required element for
   another -- there was no ordering/trimming combination found that kept
   everything.

**When one prompt genuinely cannot fit everything it needs to carry:**
- Put the higher-priority element's tags first (tokens near the front
  survive dilution better), but treat this as a mitigation, not a fix --
  it did not solve the problem in practice above.
- If two things both need reliable presence (e.g. full character identity
  AND a specific scene), consider a two-stage generation: a tight
  identity-only prompt first (full budget spent on face/hair/outfit, no
  scene tags competing), then a separate generation (e.g.
  `fal-ai/lora/inpaint`) to add the scene around the fixed identity. As of
  this writing that second stage is not yet proven reliable for scene
  fidelity -- see `businesses/somia/content/CONTENT/0007/render_two_stage.py`
  for the current attempt and its open problem.
- The more root-cause fix -- training a dedicated LoRA for a
  frequently-reused character so her identity doesn't need to be
  re-described in tokens every generation -- has been proposed but not
  yet researched or built as of this writing.

## Rule 4: watch for stray words being rendered as literal on-image text

A short, ambiguous, standalone word in a prompt (e.g. "roots" used to mean
hair-color roots) can be misread by the model as an instruction to render
a text caption/label, sometimes combined with a nearby number (e.g. a
percentage). If a generation comes back with garbled fake text/labels
somewhere in the image, check the prompt for an isolated word that could
plausibly read as a caption instruction, and reword to avoid the
standalone trigger (e.g. "dark navy roots" → "deep navy blue hair at top
blending to pale sky blue at the ends").
