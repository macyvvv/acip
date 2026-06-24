# ADR-0003: Adopt Canonical Asset Production

## Status

Proposed

## Context

ACIP requires a repeatable method for converting knowledge into durable repository-governed assets.

Conversation outputs are not stable enough to serve as canonical operational assets. Repository documents must define the asset lifecycle, review gates, and reuse rules.

## Decision

Adopt Canonical Asset Production as the current Knowledge Factory execution method.

Canonical Assets will be produced through repository-controlled templates, review checklists, WBS, and CI validation.

## Alternatives Considered

### Continue using chat outputs as the asset source

Rejected because chat is not canonical and cannot reliably support reuse, auditability, or version control.

### Move directly to runtime automation

Rejected because current phase prohibits runtime agent implementation, platform API integration, auto posting, and autonomous external actions.

### Create platform-specific content first

Rejected because platform-specific output before canonical source creation causes duplication and weakens long-term maintainability.

## Consequences

Positive:

- assets become reusable
- review becomes repeatable
- repository becomes the single source of truth
- future automation can consume stable asset definitions

Negative:

- more upfront documentation is required
- production speed is slower until templates stabilize

## Related Files

- `basis/008_canonical_asset_definition.md`
- `basis/009_asset_production_policy.md`
- `basis/010_quality_gate.md`
- `docs/CANONICAL_ASSET_TEMPLATE.md`
- `docs/ASSET_REVIEW_TEMPLATE.md`
- `wbs/WBS-0001-canonical-asset-production.md`
