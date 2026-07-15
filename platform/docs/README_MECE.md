# Documentation MECE Map

This file defines responsibility boundaries between `platform/docs/`, `platform/adr/`, and `platform/packs/`.

## Directory Responsibilities

- `platform/docs/`
  - Operational state (`platform/docs/current/`)
  - Process/runbook/checklist material
  - Human-readable explainers and references
- `platform/adr/`
  - Decision records only (why, constraints, trade-offs, acceptance)
- `platform/packs/`
  - Structured package metadata only (machine-readable)

## Placement Rule

Use this test before creating or editing a file:

1. Is it a durable decision record? -> `platform/adr/`
2. Is it structured package metadata consumed by tooling? -> `platform/packs/`
3. Is it guidance, status, or narrative explanation? -> `platform/docs/`

## Anti-duplication Rule

- Keep one canonical source per fact type:
  - Decision facts: `platform/adr/`
  - Package facts: `platform/packs/`
  - Operational guidance: `platform/docs/`
- Other locations may summarize, but should not redefine the same source-of-truth fact.

## Consolidation Pointers

- EP narrative bundle: `platform/docs/ep/EP_LEGACY_BUNDLE.md`
- Manifest bundle: `platform/docs/manifests/MANIFEST_LEGACY_BUNDLE.md`
- Pack narrative bundle: `platform/docs/platform/packs/PACKS_DOCS_LEGACY_BUNDLE.md`