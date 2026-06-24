# ADR-0016: Repository Operating System Self Test

## Status

Proposed

## Context

The ACIP repository now contains Governance, Knowledge Factory, Catalog Layer, Agent OS, Autonomous Workflow, Execution Contracts, Runtime Readiness, and validation workflows. The next risk is internal drift and Human review burden.

## Decision

Adopt Repository Operating System Self Test as a complete validation layer.

Self Test must detect:

- missing required directories and files
- broken internal markdown links
- workflow-script mismatches
- duplicate ADR/WBS IDs
- prohibited runtime actions
- Human Boundary violations
- secret-like committed strings
- orphan and dead documents
- Current Objective drift

## Human Boundary

Human should receive decision-ready reports only.

## Consequences

- Repository health becomes testable.
- Human review burden decreases.
- False positives may occur and should be triaged through issues.
- Runtime implementation remains out of scope.
