# EP-0103 File Changeset

## Create

- `contracts/WORKER_EXECUTION_CONTRACT.md`
- `workers/CODEX_WORKER_PROFILE.md`
- `workers/CHATGPT_WORKER_PROFILE.md`
- `workers/README_WORKERS.md`
- `orchestrator/WORKER_ROUTING.md`
- `specs/WORKFLOW.md`
- `specs/active/README.md`
- `specs/completed/README.md`
- `specs/archived/README.md`
- `scripts/workers/validate_worker_contracts.py`
- `scripts/specs/validate_spec_lifecycle.py`
- `scripts/validate_ep_0103.py`
- `.github/workflows/ep0103-worker-contract-layer.yml`
- `README_EP0103_WORKER_CONTRACT_LAYER.md`

## Modify if needed

- `README.md`
- `AGENTS.md`
- `orchestrator/EXECUTION_QUEUE.md`

## Forbidden Deletions

- `agent_runtime/**`
- `scripts/agent_runtime/**`
- `runtime/agent_runtime_mvp/**`
- `runtime/task_intake/**`
- existing `basis/**`
- existing `adr/**`
- existing `wbs/**`

## Implementation Notes

Use simple deterministic Python validation scripts. Do not introduce new dependencies unless already present in the repository.
