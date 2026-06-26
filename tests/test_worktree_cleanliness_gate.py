from __future__ import annotations

from orchestrator.worktree_cleanliness_gate import WorktreeCleanlinessGate


def test_worktree_cleanliness_gate_detects_repository_state() -> None:
    gate = WorktreeCleanlinessGate(".")
    result = gate.evaluate()
    assert isinstance(result.clean, bool)
