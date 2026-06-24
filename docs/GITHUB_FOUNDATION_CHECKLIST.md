# GitHub Foundation Checklist

## Conclusion

This checklist closes the bottom-layer GitHub foundation before moving to higher-order automation.

## Scope

In scope:

- Repository governance
- GitOps workflow
- Issue and PR hygiene
- CI validation
- Codex review request workflow
- Phase 0 completion evidence

Out of scope:

- Runtime agent implementation
- Auto posting
- Platform API integration
- Scraping-dependent automation
- New application frameworks

## Phase 0 Acceptance Criteria

| ID | Criterion | Required Evidence | Status |
|---|---|---|---|
| P0-01 | Repository structure is defined | `README.md`, `basis/`, `adr/`, `.github/` exist | To verify |
| P0-02 | Branch strategy is defined | branch strategy document exists | To verify |
| P0-03 | Issue templates exist | `.github/ISSUE_TEMPLATE/*.yml` | To verify |
| P0-04 | PR template exists | `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md` | To verify |
| P0-05 | ADR template exists | `adr/ADR-XXXX-template.md` or equivalent | To verify |
| P0-06 | Authority matrix exists | `basis/003_authority_matrix.md` | To verify |
| P0-07 | Responsibility matrix exists | `basis/004_responsibility_matrix.md` | To verify |
| P0-08 | Measurement definitions exist | `basis/005_measurement_definition.md` | To verify |
| P0-09 | Codex review prompt exists | codex review prompt file exists | To verify |
| P0-10 | Runtime implementation remains prohibited | `AGENTS.md` prohibition remains present | To verify |
| P0-11 | CI workflow exists | `.github/workflows/foundation-check.yml` | Missing until added |
| P0-12 | Repository hygiene check exists | `scripts/validate_foundation.py` | Missing until added |
| P0-13 | Automation scope is documented | `basis/007_automation_scope.md` | Missing until added |
| P0-14 | Automation ADR exists | `adr/ADR-0002-foundation-automation.md` | Missing until added |

## Definition of Done

Phase 0 GitHub Foundation is done when:

1. `python scripts/validate_foundation.py` exits with code 0.
2. GitHub Actions workflow `Foundation Check` passes on PR.
3. No runtime, posting, scraping, or platform API implementation is introduced.
4. Human approves the PR.
5. The PR is merged into `main`.

## Recommended Execution Order

1. Add this checklist.
2. Add automation scope document.
3. Add ADR for foundation automation.
4. Add validation script.
5. Add GitHub Actions workflow.
6. Open PR.
7. Confirm CI passes.
8. Merge after Human approval.
