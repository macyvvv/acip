# ACIP Canonical Asset Production Pack

## Conclusion

This pack defines the minimum repository documents required to execute the current objective: Canonical Asset Production.

It does not introduce runtime agents, posting automation, platform API integration, scraping, or new application frameworks.

## Files

- `basis/008_canonical_asset_definition.md`
- `basis/009_asset_production_policy.md`
- `basis/010_quality_gate.md`
- `adr/ADR-0003-canonical-asset-production.md`
- `docs/CANONICAL_ASSET_PRODUCTION_CHECKLIST.md`
- `docs/CANONICAL_ASSET_TEMPLATE.md`
- `docs/ASSET_REVIEW_TEMPLATE.md`
- `wbs/WBS-0001-canonical-asset-production.md`
- `.github/ISSUE_TEMPLATE/canonical_asset.yml`
- `.github/ISSUE_TEMPLATE/asset_review.yml`
- `scripts/validate_canonical_assets.py`
- `.github/workflows/canonical-asset-check.yml`

## Execution

1. Copy all files into the repository root.
2. Run `python scripts/validate_canonical_assets.py`.
3. Open a PR.
4. Confirm `Canonical Asset Check` passes.
5. Merge only after Human approval.

## Done Condition

The pack is complete when canonical asset documents, templates, WBS, and validation checks exist in the repository and pass CI.
