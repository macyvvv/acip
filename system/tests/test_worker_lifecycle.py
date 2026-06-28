from __future__ import annotations

from system.orchestrator.worker_lifecycle import WorkerLifecycleManager
from system.orchestrator.worker_state import WorkerState


def test_worker_lifecycle_manager_transitions_running() -> None:
    manager = WorkerLifecycleManager(".")
    state = WorkerState(worker_name="Codex", current_ep="EP-0132", queue_status="READY")
    record = manager.transition(state, "Running")
    assert record.current_state == "Running"
