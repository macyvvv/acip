# 025 Searchability Policy

## Conclusion

Searchability is a first-class requirement of Canonical Asset Production.

## Searchability Requirements

Every indexed asset should support discovery by:

- asset_id
- title
- asset_type
- category
- tags
- source_path
- lifecycle_status
- owner
- related ADR
- related WBS
- source asset id
- derivative asset id
- risk level
- value category
- review status

## Search Rules

- Repository overrides conversation.
- Asset metadata must be explicit.
- Do not rely on folder browsing alone.
- Do not rely on chat memory.
- Do not rely on implicit naming.
- Search metadata should be machine-readable where practical.
- Runtime implementation remains out of scope until approved.

## Reuse Priority

Before producing a new asset, search must attempt to find:

1. exact existing asset
2. related existing asset
3. parent asset
4. reusable derivative
5. deprecated but informative prior asset

## Human Boundary

Human should not manually search and reconcile assets when ChatGPT, Codex, scripts, or future automation can do it.
