from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from system.core.path_resolver import get_repo_root


ALLOWED_MESSAGE_TYPES = (
    "request_clarification",
    "propose_plan",
    "approve_plan",
    "reject_plan",
    "request_execution",
    "report_result",
    "request_review",
    "report_review",
    "block",
    "unblock",
    "terminate_thread",
)

ALLOWED_MESSAGE_STATUSES = (
    "draft",
    "sent",
    "received",
    "responded",
    "archived",
    "blocked",
    "terminated",
)

DEFAULT_AGENT_MESSAGES_ROOT = get_repo_root() / "system" / "runtime" / "agent_messages"


@dataclass(frozen=True)
class AgentMessage:
    message_id: str
    thread_id: str
    sender: str
    receiver: str
    message_type: str
    related_issue: str | None
    related_artifacts: tuple[str, ...] = field(default_factory=tuple)
    objective: str = ""
    requested_action: str = ""
    constraints: tuple[str, ...] = field(default_factory=tuple)
    status: str = "draft"
    created_at: str = ""
    responded_at: str | None = None
    supersedes: str | None = None
    body: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "thread_id": self.thread_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "related_issue": self.related_issue,
            "related_artifacts": list(self.related_artifacts),
            "objective": self.objective,
            "requested_action": self.requested_action,
            "constraints": list(self.constraints),
            "status": self.status,
            "created_at": self.created_at,
            "responded_at": self.responded_at,
            "supersedes": self.supersedes,
            "body": self.body,
        }


class AgentMessageContractError(ValueError):
    pass


def message_directory(base_path: Path | str | None = None, mailbox: str = "inbox") -> Path:
    root = Path(base_path) if base_path is not None else get_repo_root()
    return root / "system" / "runtime" / "agent_messages" / mailbox


def ensure_message_directories(base_path: Path | str | None = None) -> dict[str, Path]:
    directories = {
        "inbox": message_directory(base_path, "inbox"),
        "outbox": message_directory(base_path, "outbox"),
        "archive": message_directory(base_path, "archive"),
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    return directories


def validate_message_payload(payload: dict[str, Any]) -> None:
    required_fields = (
        "message_id",
        "thread_id",
        "sender",
        "receiver",
        "message_type",
        "related_issue",
        "related_artifacts",
        "objective",
        "requested_action",
        "constraints",
        "status",
        "created_at",
        "responded_at",
        "supersedes",
        "body",
    )
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise AgentMessageContractError(f"Missing required message fields: {', '.join(missing)}")
    message_type = str(payload.get("message_type", ""))
    if message_type not in ALLOWED_MESSAGE_TYPES:
        raise AgentMessageContractError(f"Unsupported message_type: {message_type}")
    status = str(payload.get("status", ""))
    if status not in ALLOWED_MESSAGE_STATUSES:
        raise AgentMessageContractError(f"Unsupported message status: {status}")
    if not isinstance(payload.get("related_artifacts"), list):
        raise AgentMessageContractError("related_artifacts must be a list")
    if not isinstance(payload.get("constraints"), list):
        raise AgentMessageContractError("constraints must be a list")


def message_from_dict(payload: dict[str, Any]) -> AgentMessage:
    validate_message_payload(payload)
    return AgentMessage(
        message_id=str(payload["message_id"]),
        thread_id=str(payload["thread_id"]),
        sender=str(payload["sender"]),
        receiver=str(payload["receiver"]),
        message_type=str(payload["message_type"]),
        related_issue=_string_or_none(payload["related_issue"]),
        related_artifacts=tuple(str(item) for item in payload["related_artifacts"]),
        objective=str(payload["objective"]),
        requested_action=str(payload["requested_action"]),
        constraints=tuple(str(item) for item in payload["constraints"]),
        status=str(payload["status"]),
        created_at=str(payload["created_at"]),
        responded_at=_string_or_none(payload["responded_at"]),
        supersedes=_string_or_none(payload["supersedes"]),
        body=str(payload["body"]),
    )


def write_message(message: AgentMessage, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(message.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def read_message(path: Path) -> AgentMessage:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AgentMessageContractError("Message payload must be a JSON object")
    return message_from_dict(payload)


def _string_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)
