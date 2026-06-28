import pytest

from system.orchestrator.queue_state import QueueState
from system.orchestrator.queue_transition import (
    QueueTransitionError,
    advance_queue_state,
    validate_queue_transition,
)


def test_validate_queue_transition_allows_linear_flow() -> None:
    validate_queue_transition("READY", "RUNNING")
    validate_queue_transition("RUNNING", "REVIEW")
    validate_queue_transition("REVIEW", "DONE")


def test_validate_queue_transition_rejects_invalid_jump() -> None:
    with pytest.raises(QueueTransitionError):
        validate_queue_transition("READY", "DONE")


def test_advance_queue_state_transitions_and_updates_next_ep() -> None:
    next_state, record = advance_queue_state(
        QueueState(status="REVIEW", active_ep="EP-0105", next_ep="EP-0106")
    )

    assert next_state.status == "DONE"
    assert next_state.active_ep == "EP-0106"
    assert record.next_status == "DONE"

