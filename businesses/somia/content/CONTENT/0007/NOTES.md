# Status: paused, 2026-07-18

This episode is **not finished** and no version currently produces a
correct render end-to-end. Read this before running anything in this
directory or trusting `script.md`/`prompt.md` at face value.

## What's actually true right now

- `script.md`'s v5 section and `prompt.md`'s v5.1 note describe the
  token-budget dilution problem as "fixed below" via tag reordering. That
  is not accurate as of this writing: after v5.1's reorder, four more
  single-stage keyframe attempts were made, and each one still sacrificed
  a different required element (scene, then outfit, then face/earring
  visibility). The reordering mitigated but did not solve the problem.
  See `.claude/skills/writing-illustrious-xl-prompts/SKILL.md` for the
  full account.
- `render_3act.py` presents itself as the active render path (its
  docstring and script.md both describe it as the current plan), but it
  is currently blocked by the token-budget issue at the keyframe step. Do
  not assume it's ready to run as-is.
- `render_two_stage.py` is the current (unfinished) attempt at a
  workaround: Stage 1 (identity-only portrait) works well. Stage 2
  (`fal-ai/lora/inpaint` scene outpainting) does not yet honor the scene
  prompt in the masked region -- it currently just extends the existing
  background color smoothly instead of generating the window/curtain/sea
  scene. `stage1_portrait.png`, `stage2_canvas.png`, `stage2_mask.png`,
  `stage2_composed.png` in this directory are that attempt's outputs, not
  a finished deliverable.

## Decision point (operator, 2026-07-18)

After the two-stage attempt's Stage 2 partially failed, the operator
decided to stop further trial-and-error prompt iteration on this episode
and move to evaluating a genuinely different method, rather than continue
tweaking prompts/staging. The leading candidate discussed but **not yet
researched or confirmed**: training a dedicated LoRA on Nao's reference
sheet images, loaded via `fal-ai/lora`'s own `loras` parameter, so her
identity is baked into model weights instead of needing full re-description
in prompt tokens on every generation. This would remove the token-budget
conflict at its root. No feasibility research (fal.ai LoRA-training
tooling, cost, turnaround time) has been done yet.

## LoRA-training feasibility research (2026-07-18, partial)

Checked fal.ai's own explore page (`fal.ai/explore/best-lora-trainers`) and
its SDXL model listings directly (primary source, not a secondary/blog
summary): fal.ai's *inference* endpoints (`fal-ai/lora`, the one already
used by this pipeline) accept a `loras` parameter to load a trained LoRA
for SDXL-family generation -- that part is confirmed and already how this
pipeline works today. But fal.ai's own dedicated **LoRA-training**
endpoint (`fal-ai/flux-lora-fast-training`) trains FLUX only. No
SDXL-family (and by extension Illustrious-XL) training endpoint was found
listed on fal.ai as of this check. This means training a Nao-specific
Illustrious-XL LoRA likely cannot be done via fal.ai's own training
tooling -- it would need a different training service or platform (e.g.
Kohya-based local/rented-GPU training, or another host's SDXL trainer)
whose output LoRA weights could then be uploaded/loaded into fal.ai's
`fal-ai/lora` inference endpoint. This has not been researched yet, and
this finding itself has not been double-checked against fal.ai's changelog
for anything added after this check -- verify current state before relying
on it.

## Before resuming work here

1. Read this file and `script.md`'s Design Note history in full.
2. Do not resume prompt-tweaking on the single-stage (`render_3act.py`) or
   two-stage (`render_two_stage.py`) pipelines as-is -- that path was
   explicitly paused, not abandoned-but-still-live.
3. If picking up the LoRA-training direction: fal.ai itself does not
   appear to offer SDXL/Illustrious-XL LoRA training (see above) -- next
   step is researching an alternative training path (cost, turnaround,
   whether the resulting weights are loadable into fal.ai's `fal-ai/lora`
   inference), not assuming fal.ai alone can do it end-to-end.
