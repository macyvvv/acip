# SUPERVISOR_LAUNCHD_SETUP

## Objective

Document the macOS supervisor launch plan without introducing launchd automation in the repository baseline.

## Current State

- No launchd automation is shipped here.
- Supervisor start remains a manual macOS operation.
- The repository provides the status export and execution request artifacts needed for review.

## Suggested macOS Launch Flow

1. Activate `.venv`.
2. Run `scripts/check_repo_os_status.sh`.
3. Start the supervisor process manually.
4. Review `runtime/operator_status/latest.md`.

## Constraints

- Do not change Repository OS architecture.
- Do not add auto-start behavior here.
- Keep launch automation separate from baseline operationalization.

## Future Approval Boundary

Any launchd/Automator implementation requires a separate approved pack.
