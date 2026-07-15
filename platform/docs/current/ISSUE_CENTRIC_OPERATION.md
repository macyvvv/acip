# ISSUE_CENTRIC_OPERATION

## Goal
Make the repository operable through GitHub Issues as the primary human-to-system interface.

The loop is:

Human → GitHub Issue → GitHub sync → Supervisor selection → Execution → Completion marker → Human review

## Operating Model

### Intake
- A human creates a GitHub Issue.
- `system/scripts/sync_github_issues.py` syncs open issues into `system/runtime/github/open_issues.json`.

### Eligibility
- The supervisor reads the synced issue mirror and repository runtime state.
- Eligible issues are selected deterministically from repository rules.

### Execution
- The selected issue is turned into an execution request.
- The local execution adapter runs the request through Claude Code (`claude -p`).

### Completion
- The processed issue is recorded in `system/runtime/issues/completed/`.
- The latest completion marker is updated in runtime artifacts.

### Human Review
- Human review uses runtime artifacts, not source code archaeology.
- Reviewers inspect sync output, supervisor output, execution output, and completion markers.

## Canonical Artifacts
- `system/runtime/github/open_issues.json`
- `system/runtime/supervisor/latest.json`
- `system/runtime/local_execution/latest.json`
- `system/runtime/local_execution/model_resolution.json`
- `system/runtime/issues/completed/issue_*.json`
- `system/runtime/handoff/completion/latest.json`

## Validation Touchpoints
- `python3 system/scripts/validate_all.py`
- Canonical pytest command from `docs/current/VALIDATION_COMMAND_POLICY.md`

## Current Assessment
- Issue intake is present.
- Issue selection is present.
- Execution plumbing is present.
- Completion markers are present.
- Human-readable operator guidance was missing and is now documented.
