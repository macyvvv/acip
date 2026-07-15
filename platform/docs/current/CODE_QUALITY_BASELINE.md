# CODE_QUALITY_BASELINE

## Scope

- `scripts/`
- `orchestrator/`
- `workers/`
- `agent_runtime/`

## Baseline Checks

- import paths are explicit and stable
- `pathlib.Path` is used for filesystem boundaries
- `dataclass` and typing are preferred for repository contracts
- `subprocess` usage is isolated to validation and orchestration boundaries
- outputs are deterministic
- validation entrypoints follow `scripts/validate_ep_*.py` patterns
- tests exist for the behavior under review
- repository-generated artifacts are kept out of the root

## Findings Policy

Findings are queued for later refactoring; they are not rewritten in this EP.
