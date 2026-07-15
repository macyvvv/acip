# Packs Docs Index

This directory stores narrative documentation for pack topics.

Canonical package metadata is not here; it is in:

- `platform/packs/registry.yaml`
- `platform/packs/PACK-*/pack.yaml`
- `platform/packs/schema/pack.schema.json`

Use this directory for:

- Human-readable background
- Cross-pack context and interpretation
- Historical rationale where an ADR is not required
- Legacy pack narratives consolidated in `PACKS_DOCS_LEGACY_BUNDLE.md`

If a change modifies package identity, dependencies, or done-conditions,
update `platform/packs/` first and then sync narrative docs here if needed.