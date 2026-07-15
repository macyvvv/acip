# AGENT_COMPLETION_CONTRACT

Repository canonical contract for machine-readable Codex completion output.

## Required Fields

- status
- pack_id
- parent_issue
- ep_id
- commit_sha
- validation_result
- pytest_result
- worktree_state
- next_action
- requires_human_approval

## Status Values

- success
- partial_success
- failure
- blocked
- skipped

## Determinism

- Completion payloads must be stable and machine-readable.
- The repository latest completion marker is the single source of truth.
