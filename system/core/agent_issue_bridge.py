from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system.core.agent_state_manager import AgentState, ensure_agent_runtime_directories, load_agent_state, write_agent_state
from system.core.agent_thread_runner import AgentThreadResult, run_agent_thread
from system.core.agent_turn_runner import run_agent_turn
from system.core.path_resolver import get_repo_root


DEFAULT_AGENT_THREADS_ROOT = get_repo_root() / "system" / "runtime" / "agent_threads"
DEFAULT_AGENT_HANDOFF_ROOT = get_repo_root() / "system" / "runtime" / "agent_handoff"


@dataclass(frozen=True)
class IssueScopedAgentBridgeResult:
    issue_scope: str
    thread_id: str
    thread_result: AgentThreadResult
    handoff_path: str | None
    request_path: str | None
    archive_path: str | None


class AgentIssueBridgeError(ValueError):
    pass


class AgentIssueBridge:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self, *, issue_number: int | None = None, approved_draft_id: str | None = None, max_turns: int = 5) -> IssueScopedAgentBridgeResult:
        if (issue_number is None) == (approved_draft_id is None):
            raise AgentIssueBridgeError("Exactly one of issue_number or approved_draft_id is required")

        ensure_agent_runtime_directories(self.base_path)
        issue_scope = self._build_issue_scope(issue_number=issue_number, approved_draft_id=approved_draft_id)
        thread_id = self._thread_id(issue_scope)
        write_agent_state(
            AgentState(
                state="waiting_for_input",
                thread_id=thread_id,
                related_issue=str(issue_scope.get("issue_number") or issue_scope.get("approved_draft_id") or ""),
                updated_at=_now(),
                transition_reason="issue-scoped bridge initialized",
            ),
            self.base_path,
        )
        inbox_path = self._thread_inbox_path(thread_id)
        self._write_thread_seed(inbox_path, issue_scope)
        thread_result = run_agent_thread(self.base_path, max_turns=max_turns)
        handoff = self._maybe_emit_handoff(issue_scope, thread_result)
        archive_path = self._archive_thread_record(issue_scope, thread_result)
        return IssueScopedAgentBridgeResult(
            issue_scope=issue_scope["issue_scope"],
            thread_id=thread_id,
            thread_result=thread_result,
            handoff_path=str(handoff) if handoff is not None else None,
            request_path=str(self._request_path()) if self._request_path().exists() else None,
            archive_path=str(archive_path) if archive_path is not None else None,
        )

    def _build_issue_scope(self, *, issue_number: int | None, approved_draft_id: str | None) -> dict[str, Any]:
        if issue_number is not None:
            issue = self._lookup_issue(issue_number)
            if issue is None:
                raise AgentIssueBridgeError(f"Issue #{issue_number} is not available for issue-scoped handoff")
            return {
                "issue_scope": f"issue:{issue_number}",
                "issue_number": issue_number,
                "issue_title": issue.get("title", ""),
                "approved_draft_id": None,
                "source": "github_issue",
            }
        draft = self._lookup_approved_draft(approved_draft_id or "")
        if draft is None:
            raise AgentIssueBridgeError(f"Approved draft {approved_draft_id} is not available for issue-scoped handoff")
        return {
            "issue_scope": f"draft:{approved_draft_id}",
            "issue_number": None,
            "issue_title": draft.get("title", ""),
            "approved_draft_id": approved_draft_id,
            "source": "approved_issue_draft",
        }

    def _lookup_issue(self, issue_number: int) -> dict[str, Any] | None:
        open_issues_path = self.base_path / "system" / "runtime" / "github" / "open_issues.json"
        if not open_issues_path.exists():
            return None
        issues = json.loads(open_issues_path.read_text(encoding="utf-8"))
        if not isinstance(issues, list):
            return None
        for issue in issues:
            if isinstance(issue, dict) and issue.get("number") == issue_number:
                return issue
        return None

    def _lookup_approved_draft(self, draft_id: str) -> dict[str, Any] | None:
        path = self.base_path / "system" / "runtime" / "research" / "approved_issue_drafts.json"
        if not path.exists():
            return None
        drafts = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(drafts, list):
            return None
        for draft in drafts:
            if isinstance(draft, dict) and draft.get("draft_id") == draft_id:
                return draft
        return None

    def _thread_id(self, issue_scope: dict[str, Any]) -> str:
        if issue_scope["issue_number"] is not None:
            return f"THREAD-ISSUE-{int(issue_scope['issue_number']):04d}"
        return f"THREAD-DRAFT-{str(issue_scope['approved_draft_id']).replace('_', '-').replace('/', '-')}"

    def _thread_inbox_path(self, thread_id: str) -> Path:
        return self.base_path / "system" / "runtime" / "agent_messages" / "inbox" / f"{thread_id}.json"

    def _write_thread_seed(self, inbox_path: Path, issue_scope: dict[str, Any]) -> None:
        inbox_path.parent.mkdir(parents=True, exist_ok=True)
        if inbox_path.exists():
            return
        payload = {
            "message_id": f"MSG-{issue_scope['issue_scope'].upper().replace(':', '-').replace('/', '-')}",
            "thread_id": self._thread_id(issue_scope),
            "sender": "ChatGPT",
            "receiver": "Codex",
            "message_type": "request_execution",
            "related_issue": str(issue_scope.get("issue_number") or issue_scope.get("approved_draft_id") or ""),
            "related_artifacts": ["docs/current/AUTONOMOUS_ISSUE_SCOPED_HANDOFF.md"],
            "objective": issue_scope["issue_title"],
            "requested_action": "issue_scoped_execution_handoff",
            "constraints": [
                "bounded",
                "deterministic",
                "no external mutation",
            ],
            "status": "received",
            "created_at": _now(),
            "responded_at": None,
            "supersedes": None,
            "body": f"Run a bounded issue-scoped thread for {issue_scope['issue_scope']}.",
        }
        inbox_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _maybe_emit_handoff(self, issue_scope: dict[str, Any], thread_result: AgentThreadResult) -> Path | None:
        if thread_result.final_state in {"blocked", "terminated"}:
            return None
        if thread_result.turns_run <= 0:
            return None
        handoff_dir = self.base_path / "system" / "runtime" / "agent_handoff"
        handoff_dir.mkdir(parents=True, exist_ok=True)
        handoff_path = handoff_dir / "latest.json"
        payload = {
            "issue_scope": issue_scope["issue_scope"],
            "issue_number": issue_scope.get("issue_number"),
            "approved_draft_id": issue_scope.get("approved_draft_id"),
            "issue_title": issue_scope.get("issue_title", ""),
            "thread_id": thread_result.thread_id,
            "thread_final_state": thread_result.final_state,
            "stop_reason": thread_result.stop_reason,
            "request_id": _request_id(issue_scope),
            "request_path": str(self._request_path()),
            "next_action": "Review the handoff and, if approved, continue through existing execution flow.",
            "created_at": _now(),
            "source": "agent_issue_bridge",
        }
        handoff_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (handoff_dir / "latest.md").write_text(_handoff_markdown(payload), encoding="utf-8")
        self._write_execution_request(payload)
        return handoff_path

    def _write_execution_request(self, handoff: dict[str, Any]) -> Path:
        request_path = self._request_path()
        request_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "request_id": handoff["request_id"],
            "request_status": "ready",
            "request_priority": 100,
            "approval_required": False,
            "dependency": [
                "system/runtime/agent_handoff/latest.json",
                "system/runtime/agent_handoff/latest.md",
                "system/runtime/agent_state/latest.json",
            ],
            "worker_assignment": "Codex",
            "next_action": handoff["next_action"],
            "objective": handoff["issue_title"],
            "issue_scope": handoff["issue_scope"],
            "issue_number": handoff.get("issue_number"),
            "approved_draft_id": handoff.get("approved_draft_id"),
        }
        request_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return request_path

    def _request_path(self) -> Path:
        return self.base_path / "system" / "runtime" / "request" / "execution_request.json"

    def _archive_thread_record(self, issue_scope: dict[str, Any], thread_result: AgentThreadResult) -> Path:
        archive_dir = self.base_path / "system" / "runtime" / "agent_threads" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "issue_scope": issue_scope["issue_scope"],
            "issue_number": issue_scope.get("issue_number"),
            "approved_draft_id": issue_scope.get("approved_draft_id"),
            "thread_id": thread_result.thread_id,
            "turns_run": thread_result.turns_run,
            "final_state": thread_result.final_state,
            "stop_reason": thread_result.stop_reason,
            "turn_results": [result.processed_message_id for result in thread_result.turn_results],
            "created_at": _now(),
        }
        archive_path = archive_dir / f"{thread_result.thread_id}.json"
        archive_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        latest_path = self.base_path / "system" / "runtime" / "agent_threads" / "latest.json"
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        latest_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (latest_path.with_suffix(".md")).write_text(_thread_markdown(record), encoding="utf-8")
        return archive_path


def _request_id(issue_scope: dict[str, Any]) -> str:
    if issue_scope.get("issue_number") is not None:
        return f"REQ-ISSUE-{int(issue_scope['issue_number']):04d}"
    return f"REQ-DRAFT-{str(issue_scope.get('approved_draft_id', '')).replace('_', '-').replace('/', '-')}"


def _handoff_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# AGENT_HANDOFF",
            "",
            f"issue_scope: {payload.get('issue_scope', '')}",
            f"issue_number: {payload.get('issue_number')}",
            f"approved_draft_id: {payload.get('approved_draft_id') or ''}",
            f"thread_id: {payload.get('thread_id', '')}",
            f"thread_final_state: {payload.get('thread_final_state', '')}",
            f"stop_reason: {payload.get('stop_reason', '')}",
            f"request_id: {payload.get('request_id', '')}",
            f"request_path: {payload.get('request_path', '')}",
            f"next_action: {payload.get('next_action', '')}",
            "",
        ]
    )


def _thread_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# AGENT_THREAD",
            "",
            f"issue_scope: {payload.get('issue_scope', '')}",
            f"issue_number: {payload.get('issue_number')}",
            f"approved_draft_id: {payload.get('approved_draft_id') or ''}",
            f"thread_id: {payload.get('thread_id', '')}",
            f"turns_run: {payload.get('turns_run', 0)}",
            f"final_state: {payload.get('final_state', '')}",
            f"stop_reason: {payload.get('stop_reason', '')}",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
