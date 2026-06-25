# WORKER_OUTPUT_SEMANTICS

Worker output status is machine-readable and deterministic.

## Statuses

- `success`: all required work completed and validation passed.
- `partial_success`: some work completed, but the output is incomplete.
- `failure`: required work did not complete or validation failed.
- `blocked`: execution cannot continue because a dependency, approval, or repository constraint is missing.
- `skipped`: execution was intentionally not performed.

## Deterministic Rule

Use the status enum before downstream consumers decide the next action.

## Next Action Rule

Consumers must select `next_action` from the status semantics table in `WORKER_OUTPUT_CONTRACT.md`.

## Contract Relation

The semantics module is the canonical machine-readable source for worker output status interpretation.
