# ACIP Asset Lifecycle Pack

## Conclusion

This pack extends Canonical Asset Production from definition into lifecycle control.

It does not introduce runtime automation, platform API integration, auto posting, scraping, or a new framework.

## Files

- `basis/011_asset_lifecycle.md`
- `basis/012_asset_repository_conventions.md`
- `adr/ADR-0004-asset-lifecycle-control.md`
- `docs/ASSET_LIFECYCLE_CHECKLIST.md`
- `docs/ASSET_STATUS_MODEL.md`
- `docs/ASSET_INDEX_TEMPLATE.md`
- `docs/ASSET_CHANGELOG_TEMPLATE.md`
- `wbs/WBS-0002-asset-lifecycle-control.md`
- `.github/ISSUE_TEMPLATE/asset_lifecycle.yml`
- `.github/workflows/asset-lifecycle-check.yml`
- `scripts/validate_asset_lifecycle.py`

## Done Condition

1. Add the files to the repository root.
2. Run `python scripts/validate_asset_lifecycle.py`.
3. Open a PR.
4. Confirm GitHub Actions workflow `Asset Lifecycle Check` passes.
5. Human approves and merges to `main`.
