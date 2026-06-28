from __future__ import annotations

from system.orchestrator.repository_state_manager import RepositoryStateManager


def test_repository_state_manager_builds_state() -> None:
    manager = RepositoryStateManager(".")
    state = manager.build_state([])
    assert state.active_ep
    assert state.next_ep
