# Architecture

## Data Flow

1. Load `runtime/planning/latest.json`.
2. Load `runtime/repository_state/latest.json`.
3. Normalize the fields needed for display.
4. Render a concise text summary.

## Responsibility Split

- Loader: read JSON artifacts from disk.
- Normalizer: extract the fields used by the renderer.
- Renderer: format the summary text.

## Decision Flow

- If a field exists, render it.
- If a field is missing, omit it rather than inventing a value.

## Test Strategy

- Unit test the renderer against representative repository-state input.
