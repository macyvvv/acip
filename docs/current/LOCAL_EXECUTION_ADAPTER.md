# LOCAL_EXECUTION_ADAPTER

## Objective

Transform supervisor execution requests into safe Codex CLI invocations and completion artifacts.

## Safety Model

- Default mode: dry-run.
- Explicit local approval flag required for real execution.
- Refuse when repository health, validation status, or worktree state is unsafe.

## Operation

1. Read execution request.
2. Validate repository context.
3. Build Codex CLI command.
4. Execute only if approval flag is set.
5. Capture completion evidence.

## Non-Goals

- No OS-level auto-start.
- No launchd / Automator integration.
- No auto-push.
- No destructive action.
