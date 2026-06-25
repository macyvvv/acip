# EP-0107 Implementation Spec

## Conclusion

Implement Worker Output Contract so Codex outputs are recorded in a machine-readable repository contract.

## Objective

Standardize Codex output format with validation results, commit SHA, worktree state, next action, and human rerun conditions.

## Required Outputs

- `orchestrator/output_contract.py`
- `docs/current/CODEX_OUTPUT_CONTRACT.md`
- `scripts/validate_ep_0107.py`
- `.github/workflows/ep0107-worker-output-contract.yml`
- `README_EP0107_WORKER_OUTPUT_CONTRACT.md`

## Constraints

- Repository remains the SSOT.
- Do not break EP-0100 through EP-0106.
- Keep validation deterministic and dependency-light.
