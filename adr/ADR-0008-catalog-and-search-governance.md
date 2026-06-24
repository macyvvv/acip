# ADR-0008: Catalog and Search Governance

## Status

Proposed

## Context

Canonical Asset Production can create, review, register, and close assets. However, long-term ROI depends on whether assets can be found, reused, combined, revised, and deprecated at scale.

## Decision

Adopt Catalog and Search Governance as a repository-governed layer for Knowledge Factory operations.

This adds:

- asset indexes by type
- category taxonomy
- tag standard
- naming standard
- search guideline
- relationship model
- catalog validation
- catalog CI workflow

## Human Boundary Decision

Human should not perform catalog hygiene, metadata normalization, or duplicate detection manually when ChatGPT, Codex, scripts, GitHub Actions, or future approved automation can perform them.

Human remains responsible for Mission, Approval, and Emergency Stop.

## Alternatives Considered

### Use only Asset Registry

Rejected because a single registry becomes insufficient as asset volume grows.

### Rely on GitHub search only

Rejected because raw search does not preserve taxonomy, relationships, lifecycle status, or reuse intent.

### Build runtime search system now

Rejected because runtime implementation remains out of scope.

## Consequences

- Searchability becomes explicit.
- Reuse becomes easier.
- Duplicate asset production should decrease.
- Additional metadata maintenance is introduced.
- Metadata maintenance should be automated wherever feasible.
