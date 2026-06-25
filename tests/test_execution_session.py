from __future__ import annotations

from orchestrator.execution_session import ExecutionSessionManager


def test_execution_session_manager_creates_and_finishes_session() -> None:
    manager = ExecutionSessionManager(".")
    session = manager.start("SESSION-1")
    finished = manager.finish(session, "completed")
    assert finished.session_status == "completed"
