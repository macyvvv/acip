# ADR Directory Scope

This directory is the decision log.

MECE boundary for repository governance artifacts:

- `platform/adr/`: decision records (why a decision was made, trade-offs, and acceptance)
- `platform/packs/`: machine-readable execution packages (`pack.yaml`, `registry.yaml`, schema)
- `platform/docs/`: operational guidance, status, runbooks, and explanatory material

Rules:

1. Put content in `platform/adr/` only when it records a durable architecture or governance decision.
2. Do not store runbook steps, checklists, or status snapshots in `platform/adr/`; put those in `platform/docs/`.
3. If a pack changes because of a decision, record the decision in `platform/adr/` and the package data in `platform/packs/`.

Cross-reference convention:

- `platform/adr/` may reference files in `platform/docs/` and `platform/packs/`.
- `platform/docs/` and `platform/packs/` should reference relevant ADRs when they depend on a specific decision.