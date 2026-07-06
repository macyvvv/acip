# Production Pipeline

## Flow

Claude Code → Script + Prompt (`somia/CONTENT/<id>/{script.md,prompt.md}`)
`system/scripts/somia/render_content.py --content-id <id>` → Video API → Output

The renderer is provider-agnostic (`system/scripts/somia/providers.py`).
`SOMIA_VIDEO_PROVIDER=dry_run` (the default) proves the pipeline without any
API key or cost. `pika` (`system/scripts/somia/providers_pika.py`) is the
first real vendor: it generates a keyframe image (fal.ai `flux/schnell`) from
the prompt's Image Prompt (KV), then animates it with Pika 2.2
image-to-video, driven by Animation/Camera Instruction. Note: Pika 2.2 only
supports 5s or 10s clips, not the spec's 12s, and does not composite the
on-screen text — that still needs a manual/scripted overlay pass. Adding a
different vendor later means one new adapter module; the script and content
specs do not change.

## Storage

- All outputs are stored in `CONTENT/`
- Inputs remain in structured spec files
- Pipeline artifacts must remain reproducible

## Control Rules

- Do not mix spec creation and content rendering
- Do not skip reviewable artifacts
- Do not hide source inputs

