# WBS-0011: Repository Operating System Self Test

## Current Phase

Knowledge Factory

## Current Objective

Repository Operating System Stabilization

## Conclusion

This WBS implements repository self-test and continuous governance.

## Scope

- Self Test policies
- Self Test ADRs
- validation scripts
- GitHub Actions workflows
- issue templates
- report templates

## Out of Scope

- runtime implementation
- auto posting
- platform API integration
- scraping-dependent automation
- external database
- new frameworks

## Work Breakdown

| ID | Task | Owner | Done Condition |
|---|---|---|---|
| WBS-0011-01 | Add Self Test policies | Codex | basis files exist |
| WBS-0011-02 | Add Self Test ADRs | Codex | ADRs exist |
| WBS-0011-03 | Add validation scripts | Codex | scripts execute |
| WBS-0011-04 | Add CI workflows | Codex | workflows exist |
| WBS-0011-05 | Add reports and templates | Codex | docs exist |

## Acceptance Criteria

- `python platform/system/platform/scripts/selftest/validate_repository_selftest_complete.py` passes.
- `Repository Self Test Complete` workflow exists.
- Runtime implementation remains out of scope.
- Human Boundary is preserved.
