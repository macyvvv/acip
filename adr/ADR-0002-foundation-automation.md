# ADR-0002: Adopt Foundation Automation

## Status

Proposed

## Context

ACIP uses GitHub as the canonical operational system. The current phase requires closing the GitHub foundation before runtime automation or higher-order architecture changes.

Manual review alone is insufficient because foundation drift can occur through small edits, missing files, or accidental introduction of prohibited Phase 0 behavior.

## Decision

Adopt a minimal GitHub Actions workflow that runs a repository foundation validation script on pull requests and manual dispatch.

The validation checks:

- required files
- required directories
- required textual anchors
- prohibited Phase 0 runtime paths
- prohibited Phase 0 behavior keywords

## Alternatives Considered

### Manual review only

Rejected. It is lower complexity but weaker against regression.

### Full CI/CD pipeline

Rejected for Phase 0. It would exceed the current objective and introduce runtime assumptions too early.

### External automation service

Rejected for Phase 0. GitHub-native automation is sufficient and keeps SSOT boundaries clear.

## Consequences

Positive:

- prevents foundation drift
- gives Codex a concrete validation target
- keeps Human approval focused
- preserves Phase 0 non-goals

Negative:

- adds one workflow and one validation script
- requires maintenance when repository conventions change

## Related Files

- `docs/GITHUB_FOUNDATION_CHECKLIST.md`
- `basis/007_automation_scope.md`
- `scripts/validate_foundation.py`
- `.github/workflows/foundation-check.yml`
