from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system.core.agent_message_contract import (
    AgentMessage,
    AgentMessageContractError,
    ensure_message_directories,
    message_from_dict,
    read_message,
    validate_message_payload,
    write_message,
)
from system.core.agent_state_manager import (
    AgentState,
    AgentStateError,
    agent_state_path,
    ensure_agent_state_files,
    load_agent_state,
    transition_agent_state,
    write_agent_state,
)
from system.core.path_resolver import get_repo_root


DEFAULT_AGENT_TURN_SUMMARY = "system/runtime/agent_state/latest.md"


@dataclass(frozen=True)
class AgentTurnResult:
    processed_message_id: str | None
    processed_message_type: str | None
    archived_message_path: str | None
    outbox_message_path: str | None
    state_path: str
    state_markdown_path: str
    next_state: str
    summary: str


class AgentTurnRunnerError(ValueError):
    pass


class AgentTurnRunner:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def _path(self, *parts: str) -> Path:
        return self.base_path / "system" / "runtime" / Path(*parts)

    def run_turn(self) -> AgentTurnResult:
        ensure_message_directories(self.base_path)
        ensure_agent_state_files(self.base_path)
        current_state = load_agent_state(self.base_path)
        inbox_messages = self._load_inbox_messages()
        if not inbox_messages:
            return self._persist_state(current_state, "idle", None, None, None, "No actionable inbox messages.")

        selected_path, selected_message = self._select_next_actionable_message(inbox_messages, current_state.thread_id)
        if selected_message is None:
            return self._persist_state(current_state, "idle", None, None, None, "No actionable inbox messages.")
        result_state, outbox_message = self._handle_message(current_state, selected_message)
        archived_path = self._archive_message(selected_path)
        outbox_path = self._emit_outbox_message(outbox_message) if outbox_message is not None else None
        return self._persist_state(
            result_state,
            result_state.state,
            selected_message.message_id,
            archived_path,
            outbox_path,
            f"Processed {selected_message.message_type} from {selected_message.sender} to {selected_message.receiver}.",
        )

    def _load_inbox_messages(self) -> list[tuple[Path, AgentMessage]]:
        inbox_dir = self._path("agent_messages", "inbox")
        messages: list[tuple[Path, AgentMessage]] = []
        for path in sorted(inbox_dir.glob("*.json")):
            try:
                message = read_message(path)
            except (AgentMessageContractError, json.JSONDecodeError):
                continue
            messages.append((path, message))
        return sorted(messages, key=lambda item: (item[1].created_at, item[1].message_id, item[0].name))

    def _select_next_actionable_message(
        self,
        inbox_messages: list[tuple[Path, AgentMessage]],
        thread_id: str | None = None,
    ) -> tuple[Path, AgentMessage] | tuple[None, None]:
        ordered_messages = inbox_messages
        if thread_id:
            ordered_messages = [item for item in inbox_messages if item[1].thread_id == thread_id]
            if not ordered_messages:
                return None, None
        for path, message in ordered_messages:
            if message.message_type in {"request_execution", "request_review", "approve_plan", "reject_plan", "block", "unblock", "terminate_thread"}:
                return path, message
        return None, None

    def _handle_message(self, current_state: AgentState, message: AgentMessage) -> tuple[AgentState, AgentMessage | None]:
        if message.message_type == "request_execution":
            return self._handle_request_execution(current_state, message)
        if message.message_type == "request_review":
            return self._handle_request_review(current_state, message)
        if message.message_type == "approve_plan":
            next_state = self._transition_or_block(current_state, "completed", "plan approved", message.message_id)
            return next_state, self._build_placeholder_reply(message, "report_review")
        if message.message_type == "reject_plan":
            next_state = self._transition_or_block(current_state, "blocked", "plan rejected", message.message_id)
            return next_state, self._build_placeholder_reply(message, "block")
        if message.message_type == "block":
            next_state = self._transition_or_block(current_state, "blocked", "received block signal", message.message_id)
            return next_state, self._build_placeholder_reply(message, "block")
        if message.message_type == "unblock":
            next_state = self._transition_or_block(current_state, "waiting_for_input", "received unblock signal", message.message_id)
            return next_state, self._build_placeholder_reply(message, "unblock")
        if message.message_type == "terminate_thread":
            next_state = AgentState(
                state="terminated",
                thread_id=message.thread_id,
                message_id=message.message_id,
                message_type=message.message_type,
                sender=message.receiver,
                receiver=message.sender,
                related_issue=message.related_issue,
                pending_messages=(),
                updated_at=_now(),
                transition_reason="thread terminated",
            )
            return next_state, self._build_placeholder_reply(message, "terminate_thread")
        raise AgentTurnRunnerError(f"Unsupported actionable message_type: {message.message_type}")

    def _handle_request_execution(self, current_state: AgentState, message: AgentMessage) -> tuple[AgentState, AgentMessage]:
        if current_state.state in {"blocked", "terminated"}:
            next_state = self._transition_or_block(current_state, current_state.state, "execution unavailable", message.message_id)
            return self._attach_message_context(next_state, message), self._build_placeholder_reply(message, "block")
        next_state = self._advance_state_path(
            current_state,
            ["ready_to_execute", "executing", "waiting_for_review"],
            reason="execution placeholder complete",
            message_id=message.message_id,
        )
        next_state = self._attach_message_context(next_state, message)
        reply = self._build_placeholder_reply(message, "report_result")
        return next_state, reply

    def _handle_request_review(self, current_state: AgentState, message: AgentMessage) -> tuple[AgentState, AgentMessage]:
        if current_state.state in {"blocked", "terminated"}:
            next_state = self._transition_or_block(current_state, current_state.state, "review unavailable", message.message_id)
            return self._attach_message_context(next_state, message), self._build_placeholder_reply(message, "block")
        if current_state.state == "waiting_for_review":
            current_state = self._attach_message_context(current_state, message)
            reply = self._build_placeholder_reply(message, "report_review")
            return current_state, reply
        if current_state.state == "executing":
            current_state = transition_agent_state(current_state, "waiting_for_review", reason="review requested", message_id=message.message_id)
        else:
            current_state = self._advance_state_path(
                current_state,
                ["waiting_for_input", "ready_to_execute", "executing", "waiting_for_review"],
                reason="review requested",
                message_id=message.message_id,
            )
        current_state = self._attach_message_context(current_state, message)
        reply = self._build_placeholder_reply(message, "report_review")
        return current_state, reply

    def _transition_or_block(self, current_state: AgentState, next_state: str, reason: str, message_id: str) -> AgentState:
        try:
            return transition_agent_state(current_state, next_state, reason=reason, message_id=message_id)
        except AgentStateError:
            return AgentState(
                state="blocked",
                thread_id=current_state.thread_id,
                message_id=message_id,
                message_type=current_state.message_type,
                sender=current_state.sender,
                receiver=current_state.receiver,
                related_issue=current_state.related_issue,
                pending_messages=current_state.pending_messages,
                updated_at=_now(),
                transition_reason=reason,
            )

    def _attach_message_context(self, state: AgentState, message: AgentMessage) -> AgentState:
        return AgentState(
            state=state.state,
            thread_id=message.thread_id,
            message_id=message.message_id,
            message_type=message.message_type,
            sender=message.sender,
            receiver=message.receiver,
            related_issue=message.related_issue,
            pending_messages=state.pending_messages,
            updated_at=state.updated_at,
            transition_reason=state.transition_reason,
        )

    def _build_placeholder_reply(self, message: AgentMessage, reply_type: str) -> AgentMessage:
        return AgentMessage(
            message_id=_message_id("reply", message.message_id),
            thread_id=message.thread_id,
            sender=message.receiver,
            receiver=message.sender,
            message_type=reply_type,
            related_issue=message.related_issue,
            related_artifacts=message.related_artifacts,
            objective=message.objective,
            requested_action=message.requested_action,
            constraints=message.constraints,
            status="sent",
            created_at=_now(),
            responded_at=None,
            supersedes=message.message_id,
            body=_placeholder_body(message, reply_type),
        )

    def _emit_outbox_message(self, message: AgentMessage) -> Path:
        outbox_dir = self._path("agent_messages", "outbox")
        outbox_dir.mkdir(parents=True, exist_ok=True)
        outbox_path = outbox_dir / f"{message.message_id}.json"
        return write_message(message, outbox_path)

    def _advance_state_path(
        self,
        current_state: AgentState,
        target_states: list[str],
        *,
        reason: str,
        message_id: str,
    ) -> AgentState:
        state = current_state
        for next_state in target_states:
            if state.state == next_state:
                continue
            state = transition_agent_state(state, next_state, reason=reason, message_id=message_id)
        return state

    def _archive_message(self, inbox_path: Path) -> Path:
        archive_dir = self._path("agent_messages", "archive")
        archive_dir.mkdir(parents=True, exist_ok=True)
        archived_path = archive_dir / inbox_path.name
        shutil.move(str(inbox_path), str(archived_path))
        return archived_path

    def _persist_state(
        self,
        state: AgentState,
        next_state: str,
        processed_message_id: str | None,
        archived_path: Path | None,
        outbox_path: Path | None,
        summary: str,
    ) -> AgentTurnResult:
        write_agent_state(state, self.base_path)
        state_path = agent_state_path(self.base_path)
        return AgentTurnResult(
            processed_message_id=processed_message_id,
            processed_message_type=state.message_type,
            archived_message_path=str(archived_path) if archived_path is not None else None,
            outbox_message_path=str(outbox_path) if outbox_path is not None else None,
            state_path=str(state_path),
            state_markdown_path=str(state_path.with_suffix(".md")),
            next_state=next_state,
            summary=summary,
        )


def run_agent_turn(base_path: str | Path = ".") -> AgentTurnResult:
    return AgentTurnRunner(base_path).run_turn()


def _message_id(prefix: str, related_id: str) -> str:
    safe_related = related_id.replace(":", "-").replace("/", "-")
    return f"{prefix}-{safe_related}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"


def _placeholder_body(message: AgentMessage, reply_type: str) -> str:
    if reply_type == "report_result":
        return f"Placeholder report_result for {message.message_id}: execution not wired yet."
    if reply_type == "report_review":
        return f"Placeholder report_review for {message.message_id}: review not wired yet."
    if reply_type == "block":
        return f"Placeholder block acknowledgement for {message.message_id}."
    if reply_type == "unblock":
        return f"Placeholder unblock acknowledgement for {message.message_id}."
    if reply_type == "terminate_thread":
        return f"Thread {message.thread_id} terminated."
    return f"Placeholder response for {message.message_id}."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
