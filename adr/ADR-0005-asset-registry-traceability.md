# ADR-0005: Asset Registry and Traceability

## Status

Proposed

## Context

Canonical Asset Production creates durable knowledge artifacts. Without a registry and traceability model, assets become hard to locate, audit, reuse, revise, or connect to ROI.

## Decision

Adopt Asset Registry and Traceability as repository-governed controls for Canonical Asset Production.

The registry will record asset metadata, lifecycle status, source path, related decisions, related WBS, and derivative relationships.

Traceability will preserve the chain from source context to canonical asset to derivative output and feedback.

## Alternatives Considered

### File discovery only

Rejected because file names and directory browsing are insufficient for reuse, auditability, and ROI tracking.

### Chat memory as registry

Rejected because repository overrides conversation and chat is not canonical.

### Runtime database

Rejected for now because runtime implementation remains out of scope.

## Consequences

- Asset reuse becomes auditable.
- Derivatives must reference source asset id.
- Revision and deprecation become controlled.
- More metadata maintenance is required.
- Runtime implementation remains out of scope.
