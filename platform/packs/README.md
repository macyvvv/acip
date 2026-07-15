# Packs Directory Scope

This directory is the package metadata layer.

MECE boundary for package-related artifacts:

- `platform/packs/`: canonical package metadata and schema
  - `platform/packs/registry.yaml`
  - `platform/packs/PACK-*/pack.yaml`
  - `platform/packs/schema/pack.schema.json`
- `platform/docs/platform/packs/`: narrative explanations for packs and historical context

Rules:

1. Treat `pack.yaml` and `registry.yaml` as source of truth for package identity, dependencies, and done-conditions.
2. Keep prose explanations in `platform/docs/platform/packs/`; avoid duplicating structured metadata there.
3. When pack metadata changes, update narrative docs only if semantics changed.

Quick navigation:

- Package metadata: `platform/packs/PACK-*`
- Narrative references: `platform/docs/platform/packs/`
- Consolidated legacy per-pack README content: `platform/packs/PACK_READMES_LEGACY_BUNDLE.md`