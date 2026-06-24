# Asset Production Operations Checklist

## Conclusion

This checklist validates that Canonical Asset Production can operate repeatedly without relying on chat memory or runtime implementation.

## Checklist

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| APO-01 | Intake policy exists | `basis/015_asset_intake_policy.md` | To verify |
| APO-02 | Production workflow exists | `basis/016_asset_production_workflow.md` | To verify |
| APO-03 | Review cadence exists | `basis/017_asset_review_cadence.md` | To verify |
| APO-04 | Output policy exists | `basis/018_asset_output_policy.md` | To verify |
| APO-05 | Operations ADR exists | `adr/ADR-0006-asset-production-operations.md` | To verify |
| APO-06 | Intake template exists | `docs/ASSET_INTAKE_TEMPLATE.md` | To verify |
| APO-07 | Triage template exists | `docs/ASSET_TRIAGE_TEMPLATE.md` | To verify |
| APO-08 | Production checklist exists | `docs/ASSET_PRODUCTION_CHECKLIST.md` | To verify |
| APO-09 | Review cadence checklist exists | `docs/ASSET_REVIEW_CADENCE_CHECKLIST.md` | To verify |
| APO-10 | Derived output template exists | `docs/DERIVED_OUTPUT_TEMPLATE.md` | To verify |
| APO-11 | WBS exists | `wbs/WBS-0004-asset-production-operations.md` | To verify |
| APO-12 | Validation script exists | `scripts/validate_asset_production_operations.py` | To verify |
| APO-13 | CI workflow exists | `.github/workflows/asset-production-operations-check.yml` | To verify |

## Definition of Done

Asset Production Operations are complete when:

1. `python scripts/validate_asset_production_operations.py` exits with code 0.
2. GitHub Actions workflow `Asset Production Operations Check` passes on PR.
3. No runtime implementation, scraping, posting, or platform API integration is introduced.
4. Human approves the PR.
5. The PR is merged into `main`.
