# EP-0103 File Changeset

## Create

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

## Modify if needed

- `README.md`
- `AGENTS.md`
- `system/orchestrator/EXECUTION_QUEUE.md`

## Forbidden Deletions

- `agent_system/runtime/**`
- `system/scripts/agent_system/runtime/**`
- `system/runtime/agent_runtime_mvp/**`
- `system/runtime/task_intake/**`
- existing `basis/**`
- existing `adr/**`
- existing `wbs/**`

## Implementation Notes

Use simple deterministic Python validation scripts. Do not introduce new dependencies unless already present in the repository.
