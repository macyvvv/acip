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

## Before resuming work here

1. Read this file and `script.md`'s Design Note history in full.
2. Do not resume prompt-tweaking on the single-stage (`render_3act.py`) or
   two-stage (`render_two_stage.py`) pipelines as-is -- that path was
   explicitly paused, not abandoned-but-still-live.
3. If picking up the LoRA-training direction, that needs its own
   feasibility research first (does fal.ai expose a LoRA-training
   endpoint for this checkpoint, cost, turnaround), not a jump straight to
   training.
