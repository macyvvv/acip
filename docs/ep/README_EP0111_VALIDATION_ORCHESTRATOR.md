# EP-0111 Validation Orchestrator

- Purpose: run all EP validation scripts and pytest from one entrypoint.
- Inputs: `scripts/validate_ep_*.py`, repository state, `pytest`.
- Outputs: `runtime/validation/validation_report.json`, `runtime/validation/VALIDATION_REPORT.md`, `docs/current/VALIDATION_STATE.md`.
- Failure mode: non-zero exit when any validation or pytest fails.
