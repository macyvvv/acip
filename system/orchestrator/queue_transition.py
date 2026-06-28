from __future__ import annotations

from dataclasses import dataclass

from system.orchestrator.queue_state import QueueState


ALLOWED_STATUSES = ("READY", "RUNNING", "REVIEW", "DONE")
ALLOWED_TRANSITIONS = {
    "READY": "RUNNING",
    "RUNNING": "REVIEW",
    "REVIEW": "DONE",
    "DONE": "DONE",
}


@dataclass(frozen=True)
class QueueTransitionResult:
    current_status: str
    next_status: str
    active_ep: str
    next_ep: str


class QueueTransitionError(ValueError):
    pass


def validate_queue_transition(current_status: str, requested_status: str) -> None:
    if current_status not in ALLOWED_STATUSES:
        raise QueueTransitionError(f"Invalid current status: {current_status}")
    if requested_status not in ALLOWED_STATUSES:
        raise QueueTransitionError(f"Invalid requested status: {requested_status}")
    expected = ALLOWED_TRANSITIONS[current_status]
    if requested_status != expected and not (current_status == requested_status == "DONE"):
        raise QueueTransitionError(
            f"Invalid queue transition: {current_status} -> {requested_status}"
        )


def advance_queue_state(state: QueueState, requested_status: str | None = None) -> tuple[QueueState, QueueTransitionResult]:
    next_status = requested_status or ALLOWED_TRANSITIONS[state.status]
    validate_queue_transition(state.status, next_status)
    next_state = QueueState(
        status=next_status,
        active_ep=state.active_ep if next_status != "DONE" else state.next_ep,
        next_ep=state.next_ep,
    )
    return next_state, QueueTransitionResult(
        current_status=state.status,
        next_status=next_status,
        active_ep=next_state.active_ep,
        next_ep=next_state.next_ep,
    )
