# ISSUE_CENTRIC_OPERATION

## Goal
Make the repository operable through GitHub Issues as the primary human-to-system interface.

The loop is:

Human → GitHub Issue → GitHub sync → Supervisor selection → Execution → Completion marker → Human review

## Operating Model

### Intake
- A human creates a GitHub Issue.
- `platform/system/scripts/sync_github_issues.py` syncs open issues into `platform/system/runtime/github/open_issues.json`.

### Eligibility
- The supervisor reads the synced issue mirror and repository runtime state.
- Eligible issues are selected deterministically from repository rules.

### Execution
- The selected issue is turned into an execution request.
- The local execution adapter runs the request through Claude Code (`claude -p`).

### Completion
- The processed issue is recorded in `platform/system/runtime/issues/completed/`.
- The latest completion marker is updated in runtime artifacts.

### Human Review
- Human review uses runtime artifacts, not source code archaeology.
- Reviewers inspect sync output, supervisor output, execution output, and completion markers.

## Canonical Artifacts
- `platform/system/runtime/github/open_issues.json`
- `platform/system/runtime/supervisor/latest.json`
- `platform/system/runtime/local_execution/latest.json`
- `platform/system/runtime/local_execution/model_resolution.json`
- `platform/system/runtime/issues/completed/issue_*.json`
- `platform/system/runtime/handoff/completion/latest.json`

## Validation Touchpoints
- `python3 platform/system/scripts/validate_all.py`
- Canonical pytest command from `platform/docs/current/VALIDATION_COMMAND_POLICY.md`

## Current Assessment
- Issue intake is present.
- Issue selection is present.
- Execution plumbing is present.
- Completion markers are present.
- Human-readable operator guidance was missing and is now documented.
