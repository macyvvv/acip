from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from system.core.agent_execution_approval import evaluate_business_agent_scope_approval
from system.core.business_agent_automation_control import automation_pause_info
from system.core.execution_pre_approval_control import pre_approval_pause_info
from system.core.publishing_control import publishing_pause_info
from system.core.business_agent_handoff import compute_request_id, load_business_agent_handoff
from system.core.business_agent_task_queue import load_queue, mark_task_status


@dataclass(frozen=True)
class ApprovalScope:
    issue_number: int | None
    scope_type: str
    scope_id: str
    title: str
    current_bucket: str
    execution_fit: str
    handoff_id: str | None
    approval_status: str
    execution_allowed: bool
    latest_execution_status: str | None
    recommendation_reason: str
    source_of_truth: str
    blocking_reason: str | None = None
    current_status: str | None = None
    approval_ready: bool = False
    business_id: str | None = None
    role_id: str | None = None
    authorization_source: str | None = None
    policy_id: str | None = None


@dataclass(frozen=True)
class ConsoleResult:
    status: str
    approval_path: str | None
    approval_reason: str | None
    execution_path: str | None
    execution_result_status: str | None
    completion_marker_path: str | None
    message: str
    zero_candidate_reason: str | None = None
    candidate_summary: str | None = None
    current_execution_target: str | None = None


class ApprovalConsoleService:
    def __init__(
        self,
        repo_root: str | Path = ".",
        executor: Callable[[list[str], Path | None], subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.executor = executor or self._run_subprocess

    def load_scopes(self) -> list[ApprovalScope]:
        roadmap = self._read_json(self.repo_root / "system" / "runtime" / "roadmap" / "issue_portfolio.json") or {}
        open_issues = self._read_json(self.repo_root / "system" / "runtime" / "github" / "open_issues.json") or []
        frozen_plan = self._read_json(self.repo_root / "system" / "runtime" / "roadmap" / "frozen_issue_closure_plan.json") or {}
        latest_execution = self._read_json(self.repo_root / "system" / "runtime" / "agent_execution" / "latest.json") or {}
        current_handoff = self._read_json(self.repo_root / "system" / "runtime" / "agent_handoff" / "latest.json") or {}
        approval = self._read_json(self.repo_root / "system" / "runtime" / "agent_handoff" / "approval.json") or {}
        completed_numbers = {
            item.get("issue_number")
            for item in self._iter_json_files(self.repo_root / "system" / "runtime" / "issues" / "completed")
            if isinstance(item.get("issue_number"), int)
        }
        open_issue_numbers = {
            item["number"]
            for item in open_issues
            if isinstance(item, dict) and isinstance(item.get("number"), int)
        }
        close_completed = {
            item["issue_number"]
            for item in frozen_plan.get("issues", [])
            if item.get("closure_disposition") == "close_completed"
        }
        roadmap_items = roadmap.get("issues", [])
        scopes: list[ApprovalScope] = []
        for item in roadmap_items:
            issue_number = item.get("issue_number")
            if item.get("priority_bucket") != "NOW":
                continue
            if item.get("execution_fit") != "one_shot_ready":
                continue
            if issue_number in completed_numbers or issue_number in close_completed:
                continue
            if issue_number not in open_issue_numbers:
                continue
            title = str(item.get("title") or "")
            scope_id = str(issue_number) if issue_number is not None else ""
            approval_ready = (
                current_handoff.get("issue_number") == issue_number
                and not current_handoff.get("approved_draft_id")
                and bool(current_handoff.get("request_id"))
            )
            scopes.append(
                ApprovalScope(
                    issue_number=issue_number,
                    scope_type="issue",
                    scope_id=scope_id,
                    title=title,
                    current_bucket=str(item.get("priority_bucket") or ""),
                    execution_fit=str(item.get("execution_fit") or ""),
                    handoff_id=str(current_handoff.get("request_id") or "") or None,
                    approval_status=str(approval.get("decision_status") or "pending"),
                    execution_allowed=bool(approval.get("execution_enabled", False)),
                    latest_execution_status=str(latest_execution.get("execution_result_status") or "") or None,
                    recommendation_reason=str(item.get("recommended_reason") or ""),
                    source_of_truth="system/runtime/roadmap/issue_portfolio.json",
                    blocking_reason=str(item.get("blocking_reason") or "") or None,
                    current_status=str(item.get("current_status") or "") or None,
                    approval_ready=approval_ready,
                )
            )

        for task in load_queue(self.repo_root):
            if task.get("status") != "candidate":
                continue
            business_id = str(task.get("business_id") or "")
            role_id = str(task.get("role_id") or "")
            task_id = str(task.get("task_id") or "")
            scope_id = f"{business_id}:{role_id}:{task_id}"
            # Level 2: each scope has its own handoff/approval/execution-result
            # files, so every candidate's status must be looked up per-scope --
            # a single shared `approval`/`latest_execution` read (as used for
            # the issue-scope loop above) would stamp every business_role_task
            # candidate with whichever scope happened to be checked last.
            scope_approval_result = evaluate_business_agent_scope_approval(business_id, role_id, task_id, self.repo_root)
            scope_approval = scope_approval_result.approval or {}
            scope_handoff_exists = load_business_agent_handoff(business_id, role_id, task_id, self.repo_root) is not None
            scope_execution = self._read_json(
                self.repo_root / "system" / "runtime" / "agent_execution" / "scopes" / business_id / role_id / task_id / "latest.json"
            ) or {}
            scopes.append(
                ApprovalScope(
                    issue_number=None,
                    scope_type="business_role_task",
                    scope_id=scope_id,
                    title=str(task.get("title") or ""),
                    current_bucket="",
                    execution_fit="one_shot_ready",
                    handoff_id=compute_request_id(business_id, role_id, task_id),
                    approval_status=str(scope_approval.get("decision_status") or "pending"),
                    execution_allowed=bool(scope_approval.get("execution_enabled", False)),
                    latest_execution_status=str(scope_execution.get("execution_result_status") or "") or None,
                    recommendation_reason="business agent task proposed via propose_task.py",
                    source_of_truth="system/runtime/business_agent_tasks/queue.json",
                    approval_ready=scope_handoff_exists,
                    business_id=business_id,
                    role_id=role_id,
                    authorization_source=str(scope_execution.get("authorization_source") or "") or None,
                    policy_id=str(scope_execution.get("policy_id") or "") or None,
                )
            )
        return scopes

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
        if scope.scope_type == "business_role_task" and scope.business_id and scope.role_id:
            task_id = scope.scope_id.split(":")[-1]
            mark_task_status(scope.business_id, scope.role_id, task_id, "approved", self.repo_root)
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
            zero_candidate_reason=None,
            candidate_summary=None,
        )

    def run_one_shot_execution(self, scope: ApprovalScope | None = None) -> ConsoleResult:
        command = [
            sys.executable,
            str(self.repo_root / "system" / "scripts" / "agent" / "run_approved_autonomous_execution.py"),
        ]
        is_business_scope = scope is not None and scope.scope_type == "business_role_task" and scope.business_id and scope.role_id
        if is_business_scope:
            task_id = scope.scope_id.split(":")[-1]
            command += ["--business-id", scope.business_id, "--role-id", scope.role_id, "--task-id", task_id]
            execution_path = (
                self.repo_root / "system" / "runtime" / "agent_execution" / "scopes" / scope.business_id / scope.role_id / task_id / "latest.json"
            )
        else:
            execution_path = self.repo_root / "system" / "runtime" / "agent_execution" / "latest.json"
        completed = self.executor(command, self.repo_root)
        execution_result = self._read_json(execution_path) or {}
        completion_marker = execution_result.get("completion_marker_path")
        if is_business_scope:
            task_id = scope.scope_id.split(":")[-1]
            mark_task_status(scope.business_id, scope.role_id, task_id, "completed", self.repo_root)
        else:
            handoff = self._read_json(self.repo_root / "system" / "runtime" / "agent_handoff" / "latest.json") or {}
            if handoff.get("business_id") and handoff.get("role_id"):
                mark_task_status(handoff["business_id"], handoff["role_id"], str(handoff.get("task_id") or ""), "completed", self.repo_root)
        return ConsoleResult(
            status=str(execution_result.get("execution_result_status") or ("success" if completed.returncode == 0 else "failure")),
            approval_path=None,
            approval_reason=None,
            execution_path=str(execution_path),
            execution_result_status=str(execution_result.get("execution_result_status") or ""),
            completion_marker_path=str(completion_marker) if completion_marker else None,
            message=str(execution_result.get("stopped_reason") or "Execution completed."),
            zero_candidate_reason=None,
            candidate_summary=None,
        )

    def render_status(self, scope: ApprovalScope | None, result: ConsoleResult | None) -> str:
        lines = ["Approval Console MVP", ""]
        pause_info = automation_pause_info(self.repo_root)
        if pause_info:
            lines.append(f"AUTOMATION PAUSED: reason={pause_info.get('reason', '')} paused_by={pause_info.get('paused_by', '')} paused_at={pause_info.get('paused_at', '')}")
            lines.append("")
        publishing_pause = publishing_pause_info(self.repo_root)
        if publishing_pause:
            lines.append(
                f"PUBLISHING PAUSED: reason={publishing_pause.get('reason', '')} "
                f"paused_by={publishing_pause.get('paused_by', '')} paused_at={publishing_pause.get('paused_at', '')}"
            )
            lines.append("")
        pre_approval_pause = pre_approval_pause_info(self.repo_root)
        if pre_approval_pause:
            lines.append(
                f"PRE-APPROVAL PAUSED: reason={pre_approval_pause.get('reason', '')} "
                f"paused_by={pre_approval_pause.get('paused_by', '')} paused_at={pre_approval_pause.get('paused_at', '')}"
            )
            lines.append("")
        last_publish_run = self._read_json(self.repo_root / "system" / "runtime" / "publishing" / "audit" / "latest.json")
        if last_publish_run:
            lines.append(
                f"Last publish run: {last_publish_run.get('finished_at', '')} "
                f"published={len(last_publish_run.get('published', []))} blocked={len(last_publish_run.get('blocked', []))}"
            )
            for item in last_publish_run.get("published", []):
                lines.append(f"  published: {item.get('business_id')}/{item.get('role_id')}/{item.get('task_id')} -> {item.get('platform')}")
            lines.append("")
        current_target = self._current_execution_target_summary()
        if scope is None:
            reason = self._zero_candidate_reason()
            lines.append("No approval-eligible scope selected.")
            if reason:
                lines.append(f"Zero-candidate reason: {reason}")
            if current_target:
                lines.append(f"Current Execution Target: {current_target}")
        else:
            lines.extend(
                [
                    f"Current NOW candidates: {self._current_now_candidate_count()}",
                    f"Current Execution Target: {current_target or 'none'}",
                    f"Scope: {scope.scope_type}:{scope.scope_id}",
                    f"Title: {scope.title}",
                    f"Issue number: {scope.issue_number if scope.issue_number is not None else ''}",
                    f"Bucket: {scope.current_bucket}",
                    f"Execution fit: {scope.execution_fit}",
                    f"Source: {scope.source_of_truth}",
                    f"Handoff: {scope.handoff_id or ''}",
                    f"Approval ready: {str(scope.approval_ready).lower()}",
                    f"Approval status: {scope.approval_status}",
                    f"Execution allowed: {str(scope.execution_allowed).lower()}",
                    f"Latest execution status: {scope.latest_execution_status or ''}",
                    f"Authorization source: {scope.authorization_source or ''}",
                    f"Policy id: {scope.policy_id or ''}",
                    f"Recommendation: {scope.recommendation_reason}",
                ]
            )
            if scope.blocking_reason:
                lines.append(f"Blocking reason: {scope.blocking_reason}")
            lines.append("")
            lines.append(f"Recommended next candidate: {self._recommended_scope_summary()}")
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
            if result.candidate_summary:
                lines.append(f"Candidate summary: {result.candidate_summary}")
            if result.current_execution_target:
                lines.append(f"Current Execution Target: {result.current_execution_target}")
            if result.zero_candidate_reason:
                lines.append(f"Zero-candidate reason: {result.zero_candidate_reason}")
        return "\n".join(lines)

    def _run_subprocess(self, command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True)

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else data

    def _iter_json_files(self, directory: Path) -> Iterable[dict]:
        if not directory.exists():
            return []
        items: list[dict] = []
        for path in sorted(directory.glob("*.json")):
            data = self._read_json(path)
            if isinstance(data, dict):
                items.append(data)
        return items

    def _zero_candidate_reason(self) -> str | None:
        roadmap = self._read_json(self.repo_root / "system" / "runtime" / "roadmap" / "issue_portfolio.json") or {}
        now_items = [item for item in roadmap.get("issues", []) if item.get("priority_bucket") == "NOW"]
        if not now_items:
            return "no NOW items"
        one_shot_ready = [item for item in now_items if item.get("execution_fit") == "one_shot_ready"]
        if not one_shot_ready:
            return "NOW exists but not one_shot_ready"
        open_issues = self._read_json(self.repo_root / "system" / "runtime" / "github" / "open_issues.json") or []
        open_issue_numbers = {
            item["number"]
            for item in open_issues
            if isinstance(item, dict) and isinstance(item.get("number"), int)
        }
        for item in one_shot_ready:
            if item.get("issue_number") not in open_issue_numbers:
                return "item missing from open_issues mirror"
        if not (self._read_json(self.repo_root / "system" / "runtime" / "agent_handoff" / "latest.json") or {}).get("request_id"):
            return "no matching handoff for approval"
        return None

    def _recommended_scope_summary(self) -> str:
        scopes = self.load_scopes()
        if not scopes:
            return "none"
        if len(scopes) == 1:
            scope = scopes[0]
            return f"{scope.scope_type}:{scope.scope_id}"
        return f"{len(scopes)} candidates"

    def _current_now_candidate_count(self) -> int:
        return len(self.load_scopes())

    def _current_execution_target_summary(self) -> str | None:
        scopes = self.load_scopes()
        if not scopes:
            return None
        if len(scopes) == 1:
            scope = scopes[0]
            issue_number = f"#{scope.issue_number}" if scope.issue_number is not None else scope.scope_id
            return f"Issue {issue_number}: {scope.title}"
        return f"{len(scopes)} NOW + one_shot_ready candidates; operator selection required"
