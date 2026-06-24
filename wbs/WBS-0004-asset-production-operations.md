# WBS-0004: Asset Production Operations

## Current Phase

Knowledge Factory

## Current Objective

Canonical Asset Production

## Conclusion

This WBS adds repeatable production operations for Canonical Assets without introducing runtime implementation.

## Scope

- Asset intake policy
- Asset production workflow
- Asset review cadence
- Asset output policy
- Intake template
- Triage template
- Production checklist
- Review cadence checklist
- Derived output template
- Validation script
- GitHub Actions workflow

## Out of Scope

- runtime implementation
- auto posting
- platform API integration
- scraping-dependent workflows
- new application frameworks
- external database

## Work Breakdown

| ID | Task | Owner | Done Condition |
|---|---|---|---|
| WBS-0004-01 | Add intake policy | Codex | Policy exists |
| WBS-0004-02 | Add production workflow | Codex | Workflow exists |
| WBS-0004-03 | Add review cadence | Codex | Cadence exists |
| WBS-0004-04 | Add output policy | Codex | Output policy exists |
| WBS-0004-05 | Add templates | Codex | Templates exist |
| WBS-0004-06 | Add validation script | Codex | Script exits 0 |
| WBS-0004-07 | Add CI workflow | Codex | Workflow runs |

## Acceptance Criteria

- `python scripts/validate_asset_production_operations.py` passes.
- `Asset Production Operations Check` passes in GitHub Actions.
- Repository remains SSOT.
- Runtime implementation remains out of scope.
