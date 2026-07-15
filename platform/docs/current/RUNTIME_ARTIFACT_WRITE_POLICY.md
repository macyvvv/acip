# RUNTIME_ARTIFACT_WRITE_POLICY

Runtime artifact writes are allowed only for explicit refresh or explicit runtime execution.

## Allowed Write Classes

- Validation report refresh
- Generated artifact refresh
- Queue/runtime state updates initiated by explicit runtime commands

## Default Rule

- `python3 scripts/validate_all.py` is read-only and must not refresh artifacts.

## Boundary

- Implicit validation must not write runtime artifacts.
- Explicit refresh commands may write only registry-approved runtime artifact paths.

