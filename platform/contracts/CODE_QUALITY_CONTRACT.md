# CODE_QUALITY_CONTRACT

Code quality baseline is repository-native and observational.

## Scope

- `system/scripts/`
- `system/orchestrator/`
- `workers/`
- `agent_system/runtime/`

## Signals

- import path discipline
- pathlib usage
- dataclass and typing usage
- subprocess boundary
- deterministic output
- validation script pattern
- test coverage presence

## Output

The baseline emits findings and a refactoring queue; it does not rewrite code.
