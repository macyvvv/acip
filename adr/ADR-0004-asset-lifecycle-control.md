# ADR-0004: Asset Lifecycle Control

## Status

Proposed

## Context

ACIP has established Canonical Asset Production. The next operational risk is uncontrolled drift after assets are created: assets may be reused, modified, deprecated, or copied without preserving source meaning.

## Decision

Adopt an explicit Canonical Asset lifecycle:

```text
Intake → Draft → Review → Approved → Canonical → Reuse → Revision → Deprecated
```

Repository paths, metadata, status definitions, and validation checks will govern lifecycle control.

## Alternatives Considered

1. Keep assets as ordinary Markdown files.
   - Rejected because reuse and revision would become hard to audit.

2. Add runtime asset management software.
   - Rejected for this phase because runtime implementation remains out of scope.

3. Use issue labels only.
   - Rejected because labels do not preserve canonical asset metadata inside the repository.

## Consequences

### Positive

- Better auditability
- Lower drift risk
- Clearer reuse path
- Stronger future automation readiness

### Negative

- More required metadata
- More review overhead
- Requires discipline in file naming and status updates

## Related Files

- `basis/008_canonical_asset_definition.md`
- `basis/009_asset_production_policy.md`
- `basis/010_quality_gate.md`
- `basis/011_asset_lifecycle.md`
- `basis/012_asset_repository_conventions.md`
