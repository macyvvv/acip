# ADR-0025: Incremental Graph and Context Diff

## Status

Proposed

## Context

Full graph generation works, but future iteration needs lightweight diff artifacts for changed repository state.

## Decision

Adopt Incremental Graph and Context Diff as derived artifacts.

## Consequences

- Review burden decreases.
- Graph updates become auditable.
- Future Agent runtime can consume deltas safely.
