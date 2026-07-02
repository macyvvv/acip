from __future__ import annotations

import json
from pathlib import Path

from system.core.agent_turn_runner import AgentTurnRunner, run_agent_turn
from system.core.agent_state_manager import load_agent_state


def _write_message(path: Path, *, message_id: str, message_type: str, sender: str, receiver: str, thread_id: str = "THR-1") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "message_id": message_id,
                "thread_id": thread_id,
                "sender": sender,
                "receiver": receiver,
                "message_type": message_type,
                "related_issue": "ISSUE-0001",
                "related_artifacts": ["docs/current/CHATGPT_CODEX_MESSAGE_CONTRACT.md"],
                "objective": "Test objective",
                "requested_action": "test",
                "constraints": ["deterministic"],
                "status": "received",
                "created_at": "2026-07-02T00:00:00Z",
                "responded_at": None,
                "supersedes": None,
                "body": "Test body",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


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


def test_single_valid_inbox_message_is_consumed_deterministically(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "001.json", message_id="MSG-001", message_type="request_execution", sender="ChatGPT", receiver="Codex")

    result = run_agent_turn(tmp_path)

    assert result.processed_message_id == "MSG-001"
    assert result.next_state == "waiting_for_review"
    assert (tmp_path / "system" / "runtime" / "agent_messages" / "archive" / "001.json").exists()
    assert not (inbox / "001.json").exists()
    assert result.outbox_message_path is not None
    outbox = json.loads(Path(result.outbox_message_path).read_text(encoding="utf-8"))
    assert outbox["message_type"] == "report_result"
    assert outbox["supersedes"] == "MSG-001"


def test_invalid_message_is_rejected_safely(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (inbox / "bad.json").write_text("not json", encoding="utf-8")

    runner = AgentTurnRunner(tmp_path)

    result = runner.run_turn()

    assert result.processed_message_id is None
    assert result.next_state == "idle"
    assert (inbox / "bad.json").exists()
    assert not (tmp_path / "system" / "runtime" / "agent_messages" / "archive" / "bad.json").exists()


def test_processed_inbox_message_is_archived(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "review.json", message_id="MSG-REVIEW", message_type="request_review", sender="Codex", receiver="ChatGPT")

    result = run_agent_turn(tmp_path)

    assert result.processed_message_id == "MSG-REVIEW"
    assert (tmp_path / "system" / "runtime" / "agent_messages" / "archive" / "review.json").exists()


def test_state_transitions_follow_defined_model(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json", state="ready_to_execute")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "001.json", message_id="MSG-001", message_type="request_execution", sender="ChatGPT", receiver="Codex")

    run_agent_turn(tmp_path)

    state = load_agent_state(tmp_path)
    assert state.state == "waiting_for_review"
    assert state.message_id == "MSG-001"


def test_terminate_thread_closes_the_thread(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "term.json", message_id="MSG-TERM", message_type="terminate_thread", sender="ChatGPT", receiver="Codex")

    result = run_agent_turn(tmp_path)

    state = load_agent_state(tmp_path)
    assert result.next_state == "terminated"
    assert state.state == "terminated"
    assert result.outbox_message_path is not None


def test_runner_processes_one_turn_only(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "001.json", message_id="MSG-001", message_type="request_execution", sender="ChatGPT", receiver="Codex")
    _write_message(inbox / "002.json", message_id="MSG-002", message_type="request_review", sender="Codex", receiver="ChatGPT")

    result = run_agent_turn(tmp_path)

    assert result.processed_message_id == "MSG-001"
    assert (inbox / "002.json").exists()
