# Catalog Layer Checklist

## Conclusion

This checklist validates that Knowledge Factory assets are discoverable and reusable.

## Checklist

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| CL-01 | Catalog policy exists | `basis/023_catalog_policy.md` | To verify |
| CL-02 | Tag policy exists | `basis/024_tag_policy.md` | To verify |
| CL-03 | Searchability policy exists | `basis/025_searchability_policy.md` | To verify |
| CL-04 | Autonomy First policy exists | `basis/026_autonomy_first_policy.md` | To verify |
| CL-05 | Catalog ADR exists | `adr/ADR-0008-catalog-and-search-governance.md` | To verify |
| CL-06 | Autonomy ADR exists | `adr/ADR-0009-autonomy-first-operating-boundary.md` | To verify |
| CL-07 | Type indexes exist | `registry/*_INDEX.md` | To verify |
| CL-08 | Catalog standards exist | `catalog/` | To verify |
| CL-09 | Catalog templates exist | `docs/` | To verify |
| CL-10 | WBS exists | `wbs/WBS-0006-catalog-layer.md` | To verify |
| CL-11 | Validation exists | `scripts/validate_catalog_layer.py` | To verify |
| CL-12 | CI exists | `.github/workflows/catalog-layer-check.yml` | To verify |

## Definition of Done

Catalog Layer is complete when:

1. `python scripts/validate_catalog_layer.py` exits with code 0.
2. GitHub Actions workflow `Catalog Layer Check` passes on PR.
3. Human is not assigned routine catalog hygiene.
4. Runtime implementation remains out of scope.
