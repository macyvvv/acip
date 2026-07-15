# ADR-0023: Task Routing

## Status

Proposed

## Context

Without explicit task routing, Human may be assigned routine work, Codex may receive ambiguous tasks, and ChatGPT may lose repository context.

## Decision

Adopt task routing rules based on actor responsibility, risk, and boundary conditions.

## Routing Principle

Routine execution should be delegated away from Human whenever safe.

## Consequences

- Human load decreases.
- Review quality improves.
- Execution contracts become easier to generate.
