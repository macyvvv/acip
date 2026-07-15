# REPOSITORY_OS_V2_RELEASE

## Objective

Freeze Repository OS v2 as the operational baseline before product development begins.

## Architecture Overview

Repository OS v2 is a projection-driven operating baseline built from authoritative repository artifacts:

- Repository Constitution
- Planning State
- Repository State
- Supervisor projection
- Work Planner projection
- Validation artifacts

## Layer Diagram

1. Constitution
2. Planning State
3. Repository State
4. Supervisor
5. Work Planner
6. Release projection

## Repository Constitution Summary

- Projection over source of truth.
- Existing SSOTs remain authoritative.
- Deterministic repository outputs.
- Human responsibility is limited to strategy, capital allocation, high-risk approval, and repository-wide architecture.

## Planning State Summary

- Mission: Build an AI Native Company.
- Current objective: Constitution v3 Freeze.
- Approved next action: repository-managed review intake.

## Repository State Summary

- Repository health: healthy.
- Runtime health: healthy.
- Validation status: success.
- Pytest status: success.

## Supervisor Summary

- Local supervisor is dry-run by default.
- Execution requires explicit approval.
- Supervisor output is repository-backed and deterministic.

## Work Planner Summary

- Candidate recommendations are projection-only.
- Recommendations are prioritized deterministically.
- High-risk candidates require review or approval.

## Supported Operating Model

- Repository artifacts are the canonical operating interface.
- ChatGPT reviews projections and approvals.
- Codex implements repository changes and validations.
- Human supplies strategy and approvals only.

## Known Limitations

- Root hygiene is warn-only for the repository-wide layout policy.
- Some automation paths remain dry-run only.
- Product development has not started.

## Remaining Approved Technical Debt

- Root hygiene migration remains staged.
- Additional operational projections may be added only when they reduce management cost.

## Root Migration Status

- Split plan defined.
- Low-risk execution scripts defined.
- High-risk migration remains approval-gated.

## Release Acceptance Criteria

- `python3 scripts/validate_all.py` passes.
- `python3 -m pytest -q` passes.
- Worktree is clean.
- Release artifacts are deterministic.

## Roadmap for Product Development

- Use Repository OS v2 as the stable baseline.
- Add product work only when operational evidence justifies it.
- Keep new work inside Packs, not ad hoc expansion.
