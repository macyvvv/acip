# ADR-0009: Autonomy First Operating Boundary

## Status

Proposed

## Context

ACIP's long-term objective is autonomous operation. Human should not be assigned routine execution work that can be delegated to ChatGPT, Codex, scripts, GitHub Actions, or future approved automation.

## Decision

Adopt Autonomy First as an operating boundary.

Human responsibilities are limited by default to:

- Mission
- Approval
- Emergency Stop
- Risk acceptance
- Capital allocation
- Final strategic judgment

All repeatable, mechanical, review-preparable, or validation-oriented work should be delegated away from Human whenever feasible.

## Current Constraint

Runtime implementation remains out of scope until explicitly approved.

Therefore, current autonomy is limited to repository-governed workflows, validation scripts, GitHub Actions, Codex implementation, and ChatGPT review / prioritization.

## Alternatives Considered

### Human performs all repository hygiene

Rejected because it does not scale and contradicts autonomy priority.

### Implement runtime autonomy immediately

Rejected because current governance prohibits runtime implementation until approved.

### Leave boundary implicit

Rejected because unclear responsibility boundaries create unnecessary Human work.

## Consequences

- Human workload should decrease.
- Documentation must identify automation/delegation candidates.
- Future automation work has a clear policy basis.
- Runtime implementation still requires approval.
