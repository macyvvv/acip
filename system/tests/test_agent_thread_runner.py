from __future__ import annotations

import json
from pathlib import Path

from system.core.agent_thread_runner import run_agent_thread
from system.core.agent_state_manager import load_agent_state


def _write_state(path: Path, state: str = "idle") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "state": state,
                "thread_id": None,
                "message_id": None,
                "message_type": None,
                "sender": None,
                "receiver": None,
                "related_issue": None,
                "pending_messages": [],
                "updated_at": "",
                "transition_reason": "",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_message(path: Path, *, message_id: str, message_type: str, sender: str, receiver: str, thread_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "message_id": message_id,
                "thread_id": thread_id,
                "sender": sender,
                "receiver": receiver,
                "message_type": message_type,
                "related_issue": "ISSUE-0003",
                "related_artifacts": ["docs/current/AUTONOMOUS_CONVERSATION_VERTICAL_SLICE.md"],
                "objective": "Bounded thread",
                "requested_action": "advance_thread",
                "constraints": ["deterministic"],
                "status": "received",
                "created_at": "2026-07-02T00:00:00Z",
                "responded_at": None,
                "supersedes": None,
                "body": "Thread message",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_bounded_thread_reaches_deterministic_final_status(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "001.json", message_id="MSG-001", message_type="request_execution", sender="ChatGPT", receiver="Codex", thread_id="THR-1")
    _write_message(inbox / "002.json", message_id="MSG-002", message_type="request_review", sender="Codex", receiver="ChatGPT", thread_id="THR-1")
    _write_message(inbox / "003.json", message_id="MSG-003", message_type="approve_plan", sender="ChatGPT", receiver="Codex", thread_id="THR-1")

    result = run_agent_thread(tmp_path, max_turns=5)

    assert result.turns_run >= 1
    assert result.final_state in {"completed", "waiting_for_review", "blocked", "terminated"}
    assert result.stop_reason in {"completed", "blocked", "terminated", "max_turns_reached", "idle"}
    assert load_agent_state(tmp_path).state == result.final_state


def test_max_turns_guard_stops_bounded_runner(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "001.json", message_id="MSG-001", message_type="request_execution", sender="ChatGPT", receiver="Codex", thread_id="THR-1")
    _write_message(inbox / "002.json", message_id="MSG-002", message_type="request_execution", sender="ChatGPT", receiver="Codex", thread_id="THR-1")

    result = run_agent_thread(tmp_path, max_turns=1)

    assert result.turns_run == 1
    assert result.stop_reason in {"max_turns_reached", "completed", "blocked", "terminated", "idle"}


def test_sample_autonomous_thread_fixture_exists() -> None:
    assert Path("system/runtime/agent_messages/inbox/sample_autonomous_thread.json").exists()
