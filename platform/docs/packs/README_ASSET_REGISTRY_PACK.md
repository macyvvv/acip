# ACIP Asset Registry Pack

## Conclusion

This pack adds Asset Registry and Traceability control for Canonical Asset Production.

## Files

- `basis/013_asset_registry_policy.md`
- `basis/014_asset_traceability_policy.md`
- `adr/ADR-0005-asset-registry-traceability.md`
- `docs/ASSET_REGISTRY_CHECKLIST.md`
- `docs/ASSET_REGISTRY_TEMPLATE.md`
- `docs/ASSET_TRACEABILITY_MAP_TEMPLATE.md`
- `registry/ASSET_REGISTRY.md`
- `wbs/WBS-0003-asset-registry-traceability.md`
- `.github/ISSUE_TEMPLATE/asset_registry.yml`
- `.github/workflows/asset-registry-check.yml`
- `scripts/validate_asset_registry.py`

## Validation

```bash
python scripts/validate_asset_registry.py
```

## Scope

This pack is governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, and new application frameworks remain out of scope.
