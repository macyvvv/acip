from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from orchestrator.constants import QUEUE_STATE_PATH, WORKER_STATE_PATH
from orchestrator.queue_state import QueueState, read_queue_state, write_queue_state
from orchestrator.worker_state import WorkerState, read_worker_state


EP_ORDER = [
    "EP-0100",
    "EP-0101",
    "EP-0102",
    "EP-0103",
    "EP-0104",
    "EP-0105",
    "EP-0106",
    "EP-0107",
    "EP-0108",
    "EP-0109",
    "EP-0110",
    "EP-0111",
    "EP-0112",
]


@dataclass(frozen=True)
class PlannerDecision:
    current_ep: str
    next_ep: str
    queue_status: str
    dependency_chain: tuple[str, ...]


class PlannerError(ValueError):
    pass


def plan_next_ep(queue_state: QueueState, worker_state: WorkerState) -> PlannerDecision:
    _validate_status(queue_state.status)
    _validate_status(worker_state.queue_status)
    if queue_state.active_ep not in EP_ORDER:
        raise PlannerError(f"Unknown active EP: {queue_state.active_ep}")
    current_index = EP_ORDER.index(queue_state.active_ep)
    if current_index + 1 >= len(EP_ORDER):
        raise PlannerError(f"No next EP available after {queue_state.active_ep}")

    next_ep = EP_ORDER[current_index + 1]
    dependency_chain = tuple(EP_ORDER[: current_index + 2])
    return PlannerDecision(
        current_ep=queue_state.active_ep,
        next_ep=next_ep,
        queue_status=queue_state.status,
        dependency_chain=dependency_chain,
    )


def load_planner_decision(base_path: str | Path = ".") -> PlannerDecision:
    root = Path(base_path)
    queue_state = read_queue_state(root / QUEUE_STATE_PATH)
    worker_state = read_worker_state(root / WORKER_STATE_PATH)
    return plan_next_ep(queue_state, worker_state)


def persist_planned_queue_state(decision: PlannerDecision, path: str | Path = "docs/current/QUEUE_STATE.md") -> None:
    write_queue_state(
        QueueState(
            status=decision.queue_status,
            active_ep=decision.current_ep,
            next_ep=decision.next_ep,
        ),
        path=path,
    )


def plan_and_persist_queue_state(base_path: str | Path = ".") -> PlannerDecision:
    root = Path(base_path)
    decision = load_planner_decision(root)
    persist_planned_queue_state(decision, root / QUEUE_STATE_PATH)
    return decision


def _validate_status(status: str) -> None:
    if status not in {"READY", "RUNNING", "REVIEW", "DONE"}:
        raise PlannerError(f"Invalid queue status: {status}")
