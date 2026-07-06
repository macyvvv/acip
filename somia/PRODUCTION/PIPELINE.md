# Production Pipeline

## Flow

Claude Code → Script + Prompt (`somia/CONTENT/<id>/{script.md,prompt.md}`)
`system/scripts/somia/render_content.py --content-id <id>` → Video API → Output

The renderer is provider-agnostic (`system/scripts/somia/providers.py`). No
vendor is chosen yet; `SOMIA_VIDEO_PROVIDER=dry_run` (the default) proves the
pipeline without any API key or cost. Choosing a vendor (Runway, etc.) means
adding one adapter class and registering it — the script and content specs
do not change.

## Storage

- All outputs are stored in `CONTENT/`
- Inputs remain in structured spec files
- Pipeline artifacts must remain reproducible

## Control Rules

- Do not mix spec creation and content rendering
- Do not skip reviewable artifacts
- Do not hide source inputs

