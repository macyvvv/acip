# WBS-0006: Catalog Layer

## Current Phase

Knowledge Factory

## Current Objective

Canonical Asset Production

## Conclusion

This WBS adds the Catalog Layer required for asset discovery, reuse, relationship mapping, and future automation readiness.

## Scope

- Catalog policy
- Tag policy
- Searchability policy
- Autonomy First policy
- Catalog ADR
- Autonomy ADR
- Type-specific indexes
- Category taxonomy
- Tag standard
- Naming standard
- Search guideline
- Relationship model
- Catalog templates
- Validation script
- CI workflow

## Out of Scope

- runtime implementation
- auto posting
- platform API integration
- scraping-dependent automation
- external database
- new application frameworks

## Work Breakdown

| ID | Task | Owner | Done Condition |
|---|---|---|---|
| WBS-0006-01 | Add catalog policies | Codex | basis files exist |
| WBS-0006-02 | Add ADRs | Codex | ADR-0008 and ADR-0009 exist |
| WBS-0006-03 | Add registry indexes | Codex | index files exist |
| WBS-0006-04 | Add catalog standards | Codex | catalog files exist |
| WBS-0006-05 | Add templates | Codex | docs exist |
| WBS-0006-06 | Add validation script | Codex | script exits 0 |
| WBS-0006-07 | Add CI workflow | Codex | workflow exists |

## Human Boundary

Human should only approve, stop, or redirect. Routine catalog hygiene should be assigned to Codex, ChatGPT, scripts, or future approved automation.

## Acceptance Criteria

- `python scripts/validate_catalog_layer.py` passes.
- `Catalog Layer Check` passes in GitHub Actions.
- Repository remains SSOT.
- Runtime implementation remains out of scope.
