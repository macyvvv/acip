# REPOSITORY_LAYOUT_CONTRACT

## Purpose

Define the canonical repository layout and root allowlist.

## Canonical Layout

- `README.md`, `AGENTS.md`, and standard tool config files may remain at root.
- `platform/docs/current` is the source of truth for current state.
- `platform/docs/ep` contains EP description documents.
- `platform/specs/EP-xxxx` contains implementation specifications.
- `contracts` contains durable contracts.
- `scripts` contains executable helpers and validation utilities.
- `orchestrator` contains orchestration components.
- `workers` contains worker registry and worker profiles.
- `runtime` contains execution outputs.
- `graph` contains knowledge graph outputs.
- `archive` contains retired or historical assets.
- `tests` contains automated tests.

## Migration Rules

- Move instead of delete.
- Keep one logical concern per migration EP.
- Separate markdown/document moves from code moves.
- Require link updates when files move.
- Treat import-path-impacting moves as a separate EP.
- Require Human approval for high-risk migrations.

## Validation Relation

Repository layout validation is report-only at first and becomes enforcing only after a later approval.
