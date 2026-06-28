# EP-0103 Implementation Spec

## Conclusion

Implement the Repository-Native Worker Architecture so workers operate from repository contracts, worker profiles, routing rules, and lifecycle-managed specifications rather than conversation context.

## Objective

Create permanent repository assets that define:

- worker responsibilities
- execution boundaries
- routing rules
- specification lifecycle
- validation requirements
- handoff rules between ChatGPT, Codex, scripts, GitHub Actions, and future workers

## Required Outputs

Codex must create or update:

- `contracts/WORKER_EXECUTION_CONTRACT.md`
- `workers/CODEX_WORKER_PROFILE.md`
- `workers/CHATGPT_WORKER_PROFILE.md`
- `workers/README_WORKERS.md`
- `system/orchestrator/WORKER_ROUTING.md`
- `specs/WORKFLOW.md`
- `specs/active/README.md`
- `specs/completed/README.md`
- `specs/archived/README.md`
- `system/scripts/workers/validate_worker_contracts.py`
- `system/scripts/specs/validate_spec_lifecycle.py`
- `system/scripts/validate_ep_0103.py`
- `.github/workflows/ep0103-worker-contract-layer.yml`
- `README_EP0103_WORKER_CONTRACT_LAYER.md`

## Constraints

- Repository overrides conversation.
- Do not delete existing runtime implementation.
- Do not introduce runtime external execution.
- Do not introduce platform API mutation.
- Do not introduce secret use.
- Do not introduce approval bypass.
- Implement minimal necessary diff.

## Target Flow

```text
Repository/contracts
Repository/workers
Repository/specs/active
        ↓
Worker reads contracts and active spec
        ↓
Worker implements allowed changes
        ↓
Validation
        ↓
Commit / Push / Report
```
