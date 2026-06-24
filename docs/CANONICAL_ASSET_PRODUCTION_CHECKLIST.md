# Canonical Asset Production Checklist

## Conclusion

This checklist defines the minimum requirements for producing Canonical Assets under the Knowledge Factory phase.

## Readiness Checklist

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| CA-01 | Canonical Asset definition exists | `basis/008_canonical_asset_definition.md` | To verify |
| CA-02 | Asset production policy exists | `basis/009_asset_production_policy.md` | To verify |
| CA-03 | Quality gate exists | `basis/010_quality_gate.md` | To verify |
| CA-04 | ADR exists | `adr/ADR-0003-canonical-asset-production.md` | To verify |
| CA-05 | Asset template exists | `docs/CANONICAL_ASSET_TEMPLATE.md` | To verify |
| CA-06 | Review template exists | `docs/ASSET_REVIEW_TEMPLATE.md` | To verify |
| CA-07 | WBS exists | `wbs/WBS-0001-canonical-asset-production.md` | To verify |
| CA-08 | Issue templates exist | `.github/ISSUE_TEMPLATE/canonical_asset.yml`, `.github/ISSUE_TEMPLATE/asset_review.yml` | To verify |
| CA-09 | CI validation exists | `.github/workflows/canonical-asset-check.yml` | To verify |
| CA-10 | Runtime prohibitions remain intact | No runtime, posting, scraping, or platform API implementation | To verify |

## Definition of Done

Canonical Asset Production is ready when:

1. `python scripts/validate_canonical_assets.py` exits with code 0.
2. GitHub Actions workflow `Canonical Asset Check` passes on PR.
3. Human approves the PR.
4. The PR is merged into `main`.

## First Production Target

The first asset should be a small Knowledge Asset with clear reuse value and low external risk.
