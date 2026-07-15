# Local Execution Adapter Contract

## Principles

- Dry-run is the default.
- Real execution requires explicit approval.
- Supervisor remains Codex-agnostic.
- Adapter refuses unsafe execution.

## Required Inputs

- `platform/system/runtime/supervisor/latest.json`
- `platform/system/runtime/repository_state/latest.json`
- `platform/system/runtime/planning/latest.json`
- `platform/system/runtime/request/execution_request.json` if available

## Required Outputs

- `platform/system/runtime/local_execution/latest.json`
- `platform/system/runtime/local_execution/latest.md`

## Required Behaviors

- Read execution request input.
- Validate against planning and repository state.
- Build Codex CLI command.
- Capture stdout, stderr, exit code, timestamps, and worktree state.
- Preserve no-auto-push policy.
