from __future__ import annotations

import pytest

from orchestrator.output_semantics import determine_worker_output_status, worker_output_semantic


def test_output_semantics_next_action() -> None:
    semantic = worker_output_semantic("success")
    assert semantic.next_action == "Proceed to review or next repository step."


def test_output_status_determination() -> None:
    assert determine_worker_output_status(has_subtasks=True, all_subtasks_routed=True) == "success"
    assert determine_worker_output_status(has_subtasks=True, all_subtasks_routed=False) == "partial_success"
    assert determine_worker_output_status(has_subtasks=True, all_subtasks_routed=True, has_errors=True) == "failure"
    assert determine_worker_output_status(has_subtasks=True, all_subtasks_routed=True, is_blocked=True) == "blocked"
    assert determine_worker_output_status(has_subtasks=True, all_subtasks_routed=True, is_skipped=True) == "skipped"


def test_output_semantics_rejects_unknown_status() -> None:
    with pytest.raises(ValueError):
        worker_output_semantic("unknown")
