# WBS-0002: Asset Lifecycle Control

## Conclusion

This WBS closes lifecycle control for Canonical Asset Production without changing the Current Objective.

## Current Phase

Knowledge Factory

## Current Objective

Canonical Asset Production

## Scope

- Define Canonical Asset lifecycle
- Define repository naming conventions
- Define status model
- Define asset index template
- Define asset changelog template
- Add lifecycle validation script
- Add lifecycle GitHub Actions check

## Out of Scope

- runtime implementation
- auto posting
- platform API integration
- scraping-dependent automation
- new frameworks
- asset database implementation

## Work Breakdown

| ID | Task | Owner | Output | Done Condition |
|---|---|---|---|---|
| WBS-0002-01 | Add lifecycle basis | Codex | `basis/011_asset_lifecycle.md` | File merged |
| WBS-0002-02 | Add repository conventions | Codex | `basis/012_asset_repository_conventions.md` | File merged |
| WBS-0002-03 | Add ADR | Codex | `adr/ADR-0004-asset-lifecycle-control.md` | File merged |
| WBS-0002-04 | Add checklist and status model | Codex | `docs/ASSET_LIFECYCLE_CHECKLIST.md`, `docs/ASSET_STATUS_MODEL.md` | Files merged |
| WBS-0002-05 | Add templates | Codex | Index and changelog templates | Files merged |
| WBS-0002-06 | Add validation | Codex | `scripts/validate_asset_lifecycle.py` | Local check passes |
| WBS-0002-07 | Add CI workflow | Codex | `.github/workflows/asset-lifecycle-check.yml` | PR check passes |

## Acceptance Criteria

- `python scripts/validate_asset_lifecycle.py` exits with code 0.
- GitHub Actions workflow `Asset Lifecycle Check` passes.
- No runtime implementation is added.
- No Current Objective change is introduced.
