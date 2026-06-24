# WBS-0012: Repository Semantic SelfTest v2

## Current Phase

Knowledge Factory

## Current Objective

Repository Operating System Stabilization

## Conclusion

This WBS replaces raw lint-style SelfTest with configuration-driven semantic repository analysis.

## Scope

- `selftest.yml`
- semantic analyzer core
- graph builder
- boundary checks
- link checks
- duplicate checks
- orphan checks
- current objective declaration parser
- report generation
- GitHub Actions workflow
- compatibility wrapper

## Out of Scope

- runtime implementation
- auto posting
- platform API integration
- scraping-dependent automation
- external database
- new framework

## Acceptance Criteria

- `python scripts/selftest_v2/validate_semantic_selftest.py` runs.
- Archive files do not cause canonical duplicate failures.
- Explanatory mentions of Current Objective do not cause drift failures.
- Boundary descriptions do not cause runtime boundary failures.
- Real missing required files, secrets, broken workflow-script links, and duplicate canonical IDs still fail.
