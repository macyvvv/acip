from __future__ import annotations

from dataclasses import dataclass

from orchestrator.queue_state import QueueState, read_queue_state, write_queue_state
from orchestrator.worker_state import WorkerState, read_worker_state, write_worker_state


@dataclass(frozen=True)
class SchedulerDecision:
    next_ep: str
    queue_status: str
    worker_name: str


def decide_next_ep(queue_state: QueueState, worker_state: WorkerState) -> SchedulerDecision:
    if queue_state.status not in {"READY", "RUNNING", "REVIEW", "DONE"}:
        raise ValueError(f"Invalid queue status: {queue_state.status}")
    if worker_state.queue_status not in {"READY", "RUNNING", "REVIEW", "DONE"}:
        raise ValueError(f"Invalid worker queue status: {worker_state.queue_status}")
    next_ep = queue_state.next_ep if queue_state.status in {"DONE", "REVIEW"} else queue_state.active_ep
    return SchedulerDecision(next_ep=next_ep, queue_status=queue_state.status, worker_name=worker_state.worker_name)


def load_scheduler_state() -> SchedulerDecision:
    queue_state = read_queue_state()
    worker_state = read_worker_state()
    return decide_next_ep(queue_state, worker_state)


def persist_scheduler_state(queue_state: QueueState, worker_state: WorkerState) -> None:
    write_queue_state(queue_state)
    write_worker_state(worker_state)
