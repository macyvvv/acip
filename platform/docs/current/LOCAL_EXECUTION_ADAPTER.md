# LOCAL_EXECUTION_ADAPTER

## Objective

Transform supervisor execution requests into safe Claude Code (`claude -p`) CLI invocations and completion artifacts.

## Safety Model

- Default mode: dry-run.
- Explicit local approval flag required for real execution.
- Refuse when repository health, validation status, or worktree state is unsafe.

## Operation

1. Read execution request.
2. Validate repository context.
3. Build Claude Code CLI command (`claude -p "<prompt>" --model <model>`).
4. Execute only if approval flag is set.
5. Capture completion evidence.

## Model Resolution

- Default model chain: `claude-haiku-4-5` (cost-optimized) → `claude-sonnet-5` → `claude-opus-4-8`.
- High-risk / architecture / approval work floors up to `claude-opus-4-8`.
- Override via request `model_override` or `CLAUDE_MODEL_OVERRIDE`; supported set via `CLAUDE_SUPPORTED_MODELS`.
- On capacity pressure the adapter falls back from the resolved model down the cost chain.

## Non-Goals

- No OS-level auto-start.
- No launchd / Automator integration.
- No auto-push.
- No destructive action.
