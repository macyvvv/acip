from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


@dataclass(frozen=True)
class ApprovalScope:
    scope_type: str
    scope_id: str
    handoff_id: str | None
    approval_status: str
    execution_allowed: bool
    latest_execution_status: str | None


@dataclass(frozen=True)
class ConsoleResult:
    status: str
    approval_path: str | None
    approval_reason: str | None
    execution_path: str | None
    execution_result_status: str | None
    completion_marker_path: str | None
    message: str


class ApprovalConsoleService:
    def __init__(
        self,
        repo_root: str | Path = ".",
        executor: Callable[[list[str], Path | None], subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.executor = executor or self._run_subprocess

    def load_scopes(self) -> list[ApprovalScope]:
        handoff = self._read_json(self.repo_root / "system" / "runtime" / "agent_handoff" / "latest.json") or {}
        approval = self._read_json(self.repo_root / "system" / "runtime" / "agent_handoff" / "approval.json") or {}
        latest_execution = self._read_json(self.repo_root / "system" / "runtime" / "agent_execution" / "latest.json") or {}
        if not handoff:
            return []
        scope_type = "approved_draft" if handoff.get("approved_draft_id") else "issue"
        scope_id = str(handoff.get("approved_draft_id") or handoff.get("issue_number") or "")
        return [
            ApprovalScope(
                scope_type=scope_type,
                scope_id=scope_id,
                handoff_id=str(handoff.get("request_id") or ""),
                approval_status=str(approval.get("decision_status") or "pending"),
                execution_allowed=bool(approval.get("execution_enabled", False)),
                latest_execution_status=str(latest_execution.get("execution_result_status") or "") or None,
            )
        ]

    def approve_scope(self, scope: ApprovalScope, approved_by: str, reason: str) -> ConsoleResult:
        command = [
            sys.executable,
            str(self.repo_root / "system" / "scripts" / "agent" / "set_execution_approval.py"),
            "--scope-type",
            scope.scope_type,
            "--scope-id",
            scope.scope_id,
            "--handoff-id",
            scope.handoff_id or "",
            "--decision-status",
            "approved",
            "--execution-enabled",
            "true",
            "--approved-by",
            approved_by,
            "--reason",
            reason,
        ]
        completed = self.executor(command, self.repo_root)
        if completed.returncode != 0:
            return ConsoleResult(
                status="denied",
                approval_path=None,
                approval_reason=completed.stderr.strip() or completed.stdout.strip() or "approval_failed",
                execution_path=None,
                execution_result_status=None,
                completion_marker_path=None,
                message="Approval update failed.",
            )
        approval_path = self.repo_root / "system" / "runtime" / "agent_handoff" / "approval.json"
        return ConsoleResult(
            status="approved",
            approval_path=str(approval_path),
            approval_reason=None,
            execution_path=None,
            execution_result_status=None,
            completion_marker_path=None,
            message="Approval artifact updated.",
        )

    def evaluate_approval(self) -> ConsoleResult:
        command = [
            sys.executable,
            str(self.repo_root / "system" / "scripts" / "agent" / "evaluate_execution_approval.py"),
        ]
        completed = self.executor(command, self.repo_root)
        allowed = completed.returncode == 0
        return ConsoleResult(
            status="allowed" if allowed else "denied",
            approval_path=str(self.repo_root / "system" / "runtime" / "agent_handoff" / "approval.json"),
            approval_reason=completed.stdout.strip() or completed.stderr.strip() or None,
            execution_path=None,
            execution_result_status=None,
            completion_marker_path=None,
            message="Approval evaluated.",
        )

    def run_one_shot_execution(self) -> ConsoleResult:
        command = [
            sys.executable,
            str(self.repo_root / "system" / "scripts" / "agent" / "run_approved_autonomous_execution.py"),
        ]
        completed = self.executor(command, self.repo_root)
        execution_path = self.repo_root / "system" / "runtime" / "agent_execution" / "latest.json"
        execution_result = self._read_json(execution_path) or {}
        completion_marker = execution_result.get("completion_marker_path")
        return ConsoleResult(
            status=str(execution_result.get("execution_result_status") or ("success" if completed.returncode == 0 else "failure")),
            approval_path=None,
            approval_reason=None,
            execution_path=str(execution_path),
            execution_result_status=str(execution_result.get("execution_result_status") or ""),
            completion_marker_path=str(completion_marker) if completion_marker else None,
            message=str(execution_result.get("stopped_reason") or "Execution completed."),
        )

    def render_status(self, scope: ApprovalScope | None, result: ConsoleResult | None) -> str:
        lines = ["Approval Console MVP", ""]
        if scope is None:
            lines.append("No approval-eligible scope selected.")
        else:
            lines.extend(
                [
                    f"Scope: {scope.scope_type}:{scope.scope_id}",
                    f"Handoff: {scope.handoff_id or ''}",
                    f"Approval status: {scope.approval_status}",
                    f"Execution allowed: {str(scope.execution_allowed).lower()}",
                    f"Latest execution status: {scope.latest_execution_status or ''}",
                ]
            )
        lines.append("")
        if result is None:
            lines.append("Result: idle")
        else:
            lines.extend(
                [
                    f"Result: {result.status}",
                    f"Message: {result.message}",
                    f"Execution path: {result.execution_path or ''}",
                    f"Completion marker: {result.completion_marker_path or ''}",
                ]
            )
        return "\n".join(lines)

    def _run_subprocess(self, command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True)

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}

