# CANONICAL_REPOSITORY_LAYOUT

The repository is normalized around a small root and responsibility-specific directories.

## Root Goal

- Keep root entries limited to repository entry points, tooling entry points, and standard configuration.

## Directory Roles

- `platform/docs/current`: current-state repository source of truth.
- `platform/docs/ep`: EP narrative and handoff documents.
- `platform/specs/EP-xxxx`: implementation specifications for each EP.
- `contracts`: stable repository contracts.
- `scripts`: executable helpers, validation, and automation.
- `orchestrator`: planning, routing, and execution coordination.
- `workers`: worker registry and capability metadata.
- `runtime`: generated execution artifacts.
- `graph`: generated knowledge graph artifacts.
- `archive`: historical or retired material.
- `tests`: validation and regression coverage.

## Canonical Root Rule

Root-level markdown should not be used for EP-specific README, MANIFEST, PACK, or report documents.

## Relation

This document is the readable summary of `platform/contracts/REPOSITORY_LAYOUT_CONTRACT.md`.
