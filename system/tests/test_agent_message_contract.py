from __future__ import annotations

from pathlib import Path

import pytest

from system.core.agent_message_contract import (
    ALLOWED_MESSAGE_TYPES,
    AgentMessage,
    AgentMessageContractError,
    ensure_message_directories,
    message_from_dict,
    read_message,
    write_message,
)


def test_agent_message_round_trip(tmp_path: Path) -> None:
    message = AgentMessage(
        message_id="MSG-0001",
        thread_id="THR-0001",
        sender="ChatGPT",
        receiver="Codex",
        message_type="request_execution",
        related_issue="ISSUE-0037",
        related_artifacts=("docs/current/CHATGPT_CODEX_MESSAGE_CONTRACT.md",),
        objective="Execute the approved repository task",
        requested_action="implement",
        constraints=("no external mutation",),
        status="sent",
        created_at="2026-07-02T00:00:00Z",
        responded_at=None,
        supersedes=None,
        body="Please implement the requested change.",
    )

    path = write_message(message, tmp_path / "system" / "runtime" / "agent_messages" / "outbox" / "MSG-0001.json")
    restored = read_message(path)

    assert restored == message


def test_message_directories_are_created(tmp_path: Path) -> None:
    directories = ensure_message_directories(tmp_path)

    assert directories["inbox"].exists()
    assert directories["outbox"].exists()
    assert directories["archive"].exists()


def test_message_validation_rejects_invalid_type() -> None:
    payload = {
        "message_id": "MSG-0002",
        "thread_id": "THR-0001",
        "sender": "ChatGPT",
        "receiver": "Codex",
        "message_type": "invalid",
        "related_issue": None,
        "related_artifacts": [],
        "objective": "",
        "requested_action": "",
        "constraints": [],
        "status": "draft",
        "created_at": "",
        "responded_at": None,
        "supersedes": None,
        "body": "",
    }

    with pytest.raises(AgentMessageContractError, match="Unsupported message_type"):
        message_from_dict(payload)


def test_allowed_message_types_are_documented() -> None:
    assert "request_execution" in ALLOWED_MESSAGE_TYPES
