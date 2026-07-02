from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system.core.path_resolver import get_repo_root


ALLOWED_AGENT_STATES = (
    "idle",
    "waiting_for_input",
    "ready_to_execute",
    "executing",
    "waiting_for_review",
    "blocked",
    "completed",
    "terminated",
)

ALLOWED_AGENT_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "idle": ("waiting_for_input", "ready_to_execute", "blocked", "terminated"),
    "waiting_for_input": ("ready_to_execute", "blocked", "terminated"),
    "ready_to_execute": ("executing", "blocked", "terminated"),
    "executing": ("waiting_for_review", "blocked", "completed", "terminated"),
    "waiting_for_review": ("completed", "blocked", "terminated"),
    "blocked": ("waiting_for_input", "terminated"),
    "completed": ("idle", "terminated"),
    "terminated": (),
}

DEFAULT_AGENT_STATE_PATH = get_repo_root() / "system" / "runtime" / "agent_state" / "latest.json"


@dataclass(frozen=True)
class AgentState:
    state: str
    thread_id: str | None = None
    message_id: str | None = None
    message_type: str | None = None
    sender: str | None = None
    receiver: str | None = None
    related_issue: str | None = None
    pending_messages: tuple[str, ...] = ()
    updated_at: str = ""
    transition_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "thread_id": self.thread_id,
            "message_id": self.message_id,
            "message_type": self.message_type,
            "sender": self.sender,
            "receiver": self.receiver,
            "related_issue": self.related_issue,
            "pending_messages": list(self.pending_messages),
            "updated_at": self.updated_at,
            "transition_reason": self.transition_reason,
        }


class AgentStateError(ValueError):
    pass


class AgentStateTransitionError(AgentStateError):
    pass


def agent_state_path(base_path: Path | str | None = None) -> Path:
    root = Path(base_path) if base_path is not None else get_repo_root()
    return root / "system" / "runtime" / "agent_state" / "latest.json"


def ensure_agent_runtime_directories(base_path: Path | str | None = None) -> dict[str, Path]:
    root = Path(base_path) if base_path is not None else get_repo_root()
    directories = {
        "messages_inbox": root / "system" / "runtime" / "agent_messages" / "inbox",
        "messages_outbox": root / "system" / "runtime" / "agent_messages" / "outbox",
        "messages_archive": root / "system" / "runtime" / "agent_messages" / "archive",
        "state": root / "system" / "runtime" / "agent_state",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    return directories


def default_agent_state() -> AgentState:
    return AgentState(state="idle", updated_at=_now())


def load_agent_state(base_path: Path | str | None = None) -> AgentState:
    path = agent_state_path(base_path)
    if not path.exists():
        return default_agent_state()
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AgentStateError("Agent state must be a JSON object")
    return agent_state_from_dict(payload)


def write_agent_state(state: AgentState, base_path: Path | str | None = None) -> Path:
    path = agent_state_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path = path.with_suffix(".md")
    md_path.write_text(agent_state_to_markdown(state), encoding="utf-8")
    return path


def agent_state_from_dict(payload: dict[str, Any]) -> AgentState:
    state = str(payload.get("state", ""))
    if state not in ALLOWED_AGENT_STATES:
        raise AgentStateError(f"Unsupported agent state: {state}")
    pending_messages = payload.get("pending_messages", [])
    if not isinstance(pending_messages, list):
        raise AgentStateError("pending_messages must be a list")
    return AgentState(
        state=state,
        thread_id=_string_or_none(payload.get("thread_id")),
        message_id=_string_or_none(payload.get("message_id")),
        message_type=_string_or_none(payload.get("message_type")),
        sender=_string_or_none(payload.get("sender")),
        receiver=_string_or_none(payload.get("receiver")),
        related_issue=_string_or_none(payload.get("related_issue")),
        pending_messages=tuple(str(item) for item in pending_messages),
        updated_at=str(payload.get("updated_at", "")),
        transition_reason=str(payload.get("transition_reason", "")),
    )


def transition_agent_state(current: AgentState, next_state: str, *, reason: str = "", message_id: str | None = None) -> AgentState:
    if next_state not in ALLOWED_AGENT_STATES:
        raise AgentStateTransitionError(f"Unsupported agent state: {next_state}")
    allowed = ALLOWED_AGENT_TRANSITIONS.get(current.state, ())
    if next_state != current.state and next_state not in allowed:
        raise AgentStateTransitionError(f"Invalid state transition: {current.state} -> {next_state}")
    return AgentState(
        state=next_state,
        thread_id=current.thread_id,
        message_id=message_id if message_id is not None else current.message_id,
        message_type=current.message_type,
        sender=current.sender,
        receiver=current.receiver,
        related_issue=current.related_issue,
        pending_messages=current.pending_messages,
        updated_at=_now(),
        transition_reason=reason,
    )


def agent_state_to_markdown(state: AgentState) -> str:
    lines = [
        "# AGENT_STATE",
        "",
        f"state: {state.state}",
        f"thread_id: {state.thread_id or ''}",
        f"message_id: {state.message_id or ''}",
        f"message_type: {state.message_type or ''}",
        f"sender: {state.sender or ''}",
        f"receiver: {state.receiver or ''}",
        f"related_issue: {state.related_issue or ''}",
        f"pending_messages: {', '.join(state.pending_messages)}",
        f"updated_at: {state.updated_at}",
        f"transition_reason: {state.transition_reason}",
        "",
    ]
    return "\n".join(lines)


def ensure_agent_state_files(base_path: Path | str | None = None) -> dict[str, Path]:
    directories = ensure_agent_runtime_directories(base_path)
    state = load_agent_state(base_path)
    state_path = agent_state_path(base_path)
    write_agent_state(state, base_path)
    return {"json": state_path, "md": state_path.with_suffix(".md"), **directories}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _string_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)
