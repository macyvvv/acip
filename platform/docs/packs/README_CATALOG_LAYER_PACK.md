# ACIP Catalog Layer Pack

## Conclusion

This pack adds Catalog, Search, Relationship, and Autonomy First governance for Knowledge Factory operations.

## Files

- `basis/023_catalog_policy.md`
- `basis/024_tag_policy.md`
- `basis/025_searchability_policy.md`
- `basis/026_autonomy_first_policy.md`
- `adr/ADR-0008-catalog-and-search-governance.md`
- `adr/ADR-0009-autonomy-first-operating-boundary.md`
- `registry/KNOWLEDGE_INDEX.md`
- `registry/CONTENT_INDEX.md`
- `registry/MEDIA_INDEX.md`
- `registry/OPERATIONAL_INDEX.md`
- `registry/DEPRECATED_INDEX.md`
- `catalog/CATEGORY_TAXONOMY.md`
- `catalog/TAG_STANDARD.md`
- `catalog/NAMING_STANDARD.md`
- `catalog/SEARCH_GUIDELINE.md`
- `catalog/RELATIONSHIP_MODEL.md`
- `docs/CATALOG_ENTRY_TEMPLATE.md`
- `docs/KNOWLEDGE_CARD_TEMPLATE.md`
- `docs/SEARCH_METADATA_TEMPLATE.md`
- `docs/CATALOG_LAYER_CHECKLIST.md`
- `wbs/WBS-0006-catalog-layer.md`
- `.github/ISSUE_TEMPLATE/catalog_update.yml`
- `.github/workflows/catalog-layer-check.yml`
- `scripts/validate_catalog_layer.py`

## Validation

```bash
python scripts/validate_catalog_layer.py
```

## Human Boundary

Human should only handle Mission, Approval, Emergency Stop, risk acceptance, capital allocation, and final strategic judgment.

Routine catalog hygiene, metadata normalization, duplicate detection, checklist execution, and validation should be delegated to ChatGPT, Codex, scripts, GitHub Actions, or future approved automation.

## Scope

Governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, external databases, architecture changes, and new frameworks remain out of scope.
