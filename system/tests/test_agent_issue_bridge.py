from __future__ import annotations

import json
from pathlib import Path

import pytest

from system.core.agent_issue_bridge import AgentIssueBridge, AgentIssueBridgeError


def _write_open_issue(path: Path, issue_number: int, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([{"number": issue_number, "title": title, "state": "open"}], indent=2), encoding="utf-8")


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


def _write_message(path: Path, *, thread_id: str, message_id: str, message_type: str, sender: str, receiver: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "message_id": message_id,
                "thread_id": thread_id,
                "sender": sender,
                "receiver": receiver,
                "message_type": message_type,
                "related_issue": "30",
                "related_artifacts": ["docs/current/AUTONOMOUS_ISSUE_SCOPED_HANDOFF.md"],
                "objective": "Issue scoped test",
                "requested_action": "run",
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


def test_explicit_issue_scope_required(tmp_path: Path) -> None:
    bridge = AgentIssueBridge(tmp_path)

    with pytest.raises(AgentIssueBridgeError, match="Exactly one"):
        bridge.run()


def test_issue_scoped_thread_produces_handoff_artifact(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    _write_open_issue(tmp_path / "system" / "runtime" / "github" / "open_issues.json", 30, "PRODUCT-0001: Product Launch Checklist")

    result = AgentIssueBridge(tmp_path).run(issue_number=30, max_turns=3)

    assert result.issue_scope == "issue:30"
    assert result.thread_result.turns_run >= 1
    assert (tmp_path / "system" / "runtime" / "agent_threads" / "latest.json").exists()
    assert (tmp_path / "system" / "runtime" / "agent_threads" / "latest.md").exists()
    assert (tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json").exists()
    assert (tmp_path / "system" / "runtime" / "request" / "execution_request.json").exists()


def test_blocked_thread_produces_no_execution_handoff(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    _write_open_issue(tmp_path / "system" / "runtime" / "github" / "open_issues.json", 30, "PRODUCT-0001: Product Launch Checklist")
    inbox = tmp_path / "system" / "runtime" / "agent_messages" / "inbox"
    _write_message(inbox / "THREAD-ISSUE-0030.json", thread_id="THREAD-ISSUE-0030", message_id="MSG-BLOCK", message_type="block", sender="ChatGPT", receiver="Codex")

    result = AgentIssueBridge(tmp_path).run(issue_number=30, max_turns=1)

    assert result.thread_result.final_state == "blocked"
    assert result.handoff_path is None
    assert not (tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json").exists()


def test_archive_state_outputs_are_updated(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    _write_open_issue(tmp_path / "system" / "runtime" / "github" / "open_issues.json", 30, "PRODUCT-0001: Product Launch Checklist")

    result = AgentIssueBridge(tmp_path).run(issue_number=30, max_turns=1)

    assert result.archive_path is not None
    assert Path(result.archive_path).exists()
    assert (tmp_path / "system" / "runtime" / "agent_threads" / "latest.json").exists()
    assert (tmp_path / "system" / "runtime" / "agent_threads" / "latest.md").exists()


def test_max_turns_guard_works(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    _write_open_issue(tmp_path / "system" / "runtime" / "github" / "open_issues.json", 30, "PRODUCT-0001: Product Launch Checklist")

    result = AgentIssueBridge(tmp_path).run(issue_number=30, max_turns=1)

    assert result.thread_result.turns_run == 1


def test_no_github_mutation_occurs(tmp_path: Path) -> None:
    _write_state(tmp_path / "system" / "runtime" / "agent_state" / "latest.json")
    _write_open_issue(tmp_path / "system" / "runtime" / "github" / "open_issues.json", 30, "PRODUCT-0001: Product Launch Checklist")
    before = (tmp_path / "system" / "runtime" / "github" / "open_issues.json").read_text(encoding="utf-8")

    AgentIssueBridge(tmp_path).run(issue_number=30, max_turns=1)

    after = (tmp_path / "system" / "runtime" / "github" / "open_issues.json").read_text(encoding="utf-8")
    assert before == after
