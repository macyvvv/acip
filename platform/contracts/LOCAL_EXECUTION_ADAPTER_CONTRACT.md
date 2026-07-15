# Local Execution Adapter Contract

## Principles

- Dry-run is the default.
- Real execution requires explicit approval.
- Supervisor remains Codex-agnostic.
- Adapter refuses unsafe execution.

## Required Inputs

- `system/runtime/supervisor/latest.json`
- `system/runtime/repository_state/latest.json`
- `system/runtime/planning/latest.json`
- `system/runtime/request/execution_request.json` if available

## Required Outputs

- `system/runtime/local_execution/latest.json`
- `system/runtime/local_execution/latest.md`

## Required Behaviors

- Read execution request input.
- Validate against planning and repository state.
- Build Codex CLI command.
- Capture stdout, stderr, exit code, timestamps, and worktree state.
- Preserve no-auto-push policy.
