# EP-0105 Implementation Spec

## Conclusion

Implement Repository Scheduler & Dispatcher so queue and worker state are tracked in the repository and next EP selection is deterministic.

## Objective

Create repository-managed queue state, worker state, and scheduler decision logic with minimal supporting validation.

## Required Outputs

- `docs/current/QUEUE_STATE.md`
- `docs/current/WORKER_STATE.md`
- `orchestrator/queue_state.py`
- `orchestrator/worker_state.py`
- `orchestrator/scheduler.py`
- `scripts/validate_ep_0105.py`
- `.github/workflows/ep0105-scheduler-dispatcher.yml`
- `README_EP0105_REPOSITORY_SCHEDULER_DISPATCHER.md`

## Constraints

- Repository remains the SSOT.
- Queue status values are READY, RUNNING, REVIEW, DONE.
- Do not break EP-0100 through EP-0104.
