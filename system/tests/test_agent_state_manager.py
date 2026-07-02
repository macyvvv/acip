from __future__ import annotations

from pathlib import Path

import pytest

from system.core.agent_state_manager import (
    AgentState,
    AgentStateTransitionError,
    agent_state_from_dict,
    ensure_agent_runtime_directories,
    load_agent_state,
    transition_agent_state,
    write_agent_state,
)


def test_agent_state_round_trip(tmp_path: Path) -> None:
    state = AgentState(
        state="waiting_for_input",
        thread_id="THR-0001",
        message_id="MSG-0001",
        message_type="request_clarification",
        sender="ChatGPT",
        receiver="Codex",
        related_issue="ISSUE-0037",
        pending_messages=("MSG-0002",),
        updated_at="2026-07-02T00:00:00Z",
        transition_reason="waiting on clarification",
    )

    path = write_agent_state(state, tmp_path)
    restored = load_agent_state(tmp_path)

    assert path.exists()
    assert path.with_suffix(".md").exists()
    assert restored == state


def test_agent_state_directories_are_created(tmp_path: Path) -> None:
    directories = ensure_agent_runtime_directories(tmp_path)

    assert directories["messages_inbox"].exists()
    assert directories["messages_outbox"].exists()
    assert directories["messages_archive"].exists()
    assert directories["state"].exists()


def test_agent_state_transition_rules() -> None:
    current = AgentState(state="idle")
    next_state = transition_agent_state(current, "waiting_for_input", reason="waiting on human")

    assert next_state.state == "waiting_for_input"
    assert next_state.transition_reason == "waiting on human"


def test_agent_state_rejects_invalid_transition() -> None:
    current = AgentState(state="terminated")

    with pytest.raises(AgentStateTransitionError, match="Invalid state transition"):
        transition_agent_state(current, "executing")


def test_agent_state_from_dict_rejects_invalid_state() -> None:
    with pytest.raises(ValueError, match="Unsupported agent state"):
        agent_state_from_dict({"state": "unknown", "pending_messages": []})
