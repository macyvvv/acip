# LOCAL_EXECUTION_MODEL_RESOLUTION

## Objective
Resolve the lowest-cost sufficient Codex model at runtime for the local execution adapter.

## Policy

- Default policy: `cost_optimized`
- Explicit local override wins when supported
- Compatible mini model is preferred for normal tasks
- High reasoning is reserved for approved work that warrants it
- Fail closed when no compatible model can be resolved

## Resolution Fields

- `model_policy`
- `resolved_model`
- `model_resolution_reason`
- `supported_models`
- `source_artifacts`

## Default Resolution

- `gpt-5.4-mini`

## Compatibility Note

- The adapter must not hard-code `gpt-5.2`.
- The resolved model is passed to `codex exec -m <model>`.
