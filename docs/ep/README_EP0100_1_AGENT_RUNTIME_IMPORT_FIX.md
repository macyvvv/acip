# EP-0100.1 Agent Runtime MVP Import Fix

## Conclusion

This patch fixes `ModuleNotFoundError: No module named 'agent_runtime'`.

## Cause

The scripts under `scripts/agent_runtime/` were executed directly. In that mode, Python sets `sys.path[0]` to `scripts/agent_runtime`, not the repository root, so the top-level `agent_runtime/` package was not importable.

## Fix

The affected entrypoint scripts now insert Repository root into `sys.path` before importing `agent_runtime`.

## Validation

```bash
python scripts/validate_ep_0100.py
```

## Boundary

Dry run only. No external runtime execution.
