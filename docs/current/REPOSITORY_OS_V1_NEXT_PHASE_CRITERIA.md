# REPOSITORY_OS_V1_NEXT_PHASE_CRITERIA

## Entry Criteria for Next Phase

- Repository OS v1 completion review is accepted.
- Root hygiene remains classified and tracked.
- Generated artifact handling is stable enough for incremental cleanup.
- Validation and pytest continue to pass through `scripts/validate_all.py` and `python -m pytest -q`.

## Exit Criteria for Next Phase

- Root layout migration is planned as a separate EP.
- Any high-risk repository-wide change has an explicit approval path.
- New capabilities are added through repository-managed contracts and runtime state.
- Human responsibilities remain limited to strategy, approval, and capital allocation.

## Preferred Next Direction

- Reduce root warning noise with a dedicated migration EP.
- Tighten generated artifact hygiene without changing runtime semantics.
- Expand repository-managed runtime only when a new capability is justified by the current objective.

