# ACIP Asset Production Operations Pack

## Conclusion

This pack adds repeatable production operations for Canonical Asset Production.

## Files

- `basis/015_asset_intake_policy.md`
- `basis/016_asset_production_workflow.md`
- `basis/017_asset_review_cadence.md`
- `basis/018_asset_output_policy.md`
- `adr/ADR-0006-asset-production-operations.md`
- `docs/ASSET_INTAKE_TEMPLATE.md`
- `docs/ASSET_TRIAGE_TEMPLATE.md`
- `docs/ASSET_PRODUCTION_CHECKLIST.md`
- `docs/ASSET_REVIEW_CADENCE_CHECKLIST.md`
- `docs/DERIVED_OUTPUT_TEMPLATE.md`
- `docs/ASSET_PRODUCTION_OPERATIONS_CHECKLIST.md`
- `wbs/WBS-0004-asset-production-operations.md`
- `.github/ISSUE_TEMPLATE/asset_intake.yml`
- `.github/ISSUE_TEMPLATE/asset_review_cadence.yml`
- `.github/workflows/asset-production-operations-check.yml`
- `scripts/validate_asset_production_operations.py`

## Validation

```bash
python scripts/validate_asset_production_operations.py
```

## Scope

Governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, external databases, and new frameworks remain out of scope.
