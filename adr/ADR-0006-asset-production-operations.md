# ADR-0006: Asset Production Operations

## Status

Proposed

## Context

ACIP has defined Canonical Assets, lifecycle control, registry control, and traceability. The next requirement is an operational document set that allows repeatable asset production without introducing runtime automation or platform integration.

## Decision

Adopt Asset Production Operations as a repository-governed control set.

This includes:

- intake policy
- production workflow
- review cadence
- output policy
- intake templates
- production checklist
- review cadence checklist
- output template
- validation automation

## Alternatives Considered

### Continue producing assets manually without operations docs

Rejected because it does not scale and creates review inconsistency.

### Build runtime production system now

Rejected because runtime implementation remains out of scope.

### Use chat as the operating layer

Rejected because repository overrides conversation.

## Consequences

- Asset production becomes repeatable.
- Review and reuse become more consistent.
- Additional documentation overhead is introduced.
- Runtime implementation remains out of scope.
