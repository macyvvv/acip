# Asset Registry Checklist

## Conclusion

This checklist closes registry and traceability control for Canonical Asset Production.

## Checklist

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AR-01 | Registry policy exists | `basis/013_asset_registry_policy.md` | To verify |
| AR-02 | Traceability policy exists | `basis/014_asset_traceability_policy.md` | To verify |
| AR-03 | Registry ADR exists | `adr/ADR-0005-asset-registry-traceability.md` | To verify |
| AR-04 | Registry template exists | `docs/ASSET_REGISTRY_TEMPLATE.md` | To verify |
| AR-05 | Traceability map template exists | `docs/ASSET_TRACEABILITY_MAP_TEMPLATE.md` | To verify |
| AR-06 | Registry index exists | `registry/ASSET_REGISTRY.md` | To verify |
| AR-07 | Validation script exists | `scripts/validate_asset_registry.py` | To verify |
| AR-08 | CI workflow exists | `.github/workflows/asset-registry-check.yml` | To verify |
| AR-09 | Runtime remains out of scope | No runtime implementation introduced | To verify |

## Definition of Done

Asset Registry control is done when:

1. `python scripts/validate_asset_registry.py` exits with code 0.
2. GitHub Actions workflow `Asset Registry Check` passes on PR.
3. Registry and traceability files exist.
4. No runtime implementation, scraping, posting, or platform API integration is introduced.
5. Human approves the PR.
6. The PR is merged into `main`.
