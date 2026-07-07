from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from system.core.agent_execution_approval import evaluate_execution_approval
from system.orchestrator.business_agent_execution_adapter import BusinessAgentExecutionAdapter
from system.orchestrator.local_execution_adapter import LocalExecutionAdapter


@dataclass(frozen=True)
class ApprovedAutonomousExecutionResult:
    allow: bool
    handoff_id: str | None
    approval_id: str | None
    scope_type: str | None
    scope_id: str | None
    execution_triggered: bool
    execution_mode: str
    execution_result_status: str
    completion_marker_path: str | None
    request_path: str | None
    stopped_reason: str
    started_at: str
    finished_at: str


class ApprovedAutonomousExecutionError(ValueError):
    pass


class ApprovedAutonomousExecution:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self) -> ApprovedAutonomousExecutionResult:
        started_at = _now()
        approval_result = evaluate_execution_approval(self.base_path)
        handoff = approval_result.handoff or {}
        approval = approval_result.approval or {}
        if not approval_result.allowed:
            result = self._result(
                allow=False,
                handoff=handoff,
                approval=approval,
                execution_triggered=False,
                execution_mode="denied",
                execution_result_status="denied",
                completion_marker_path=None,
                request_path=self._request_path(),
                stopped_reason=approval_result.reason,
                started_at=started_at,
                finished_at=_now(),
            )
            self._write_runtime(result)
            return result

        request_path = self._request_path()
        if handoff.get("business_id") and handoff.get("role_id"):
            return self._run_business_agent(handoff, approval, request_path, started_at)

        adapter = LocalExecutionAdapter(self.base_path)
        try:
            adapter.run(approval_flag=True, dry_run=False)
        except Exception as exc:  # bounded one-shot wrapper; stop safely on any failure
            completion_marker_path = self._completion_marker_path()
            result = self._result(
                allow=True,
                handoff=handoff,
                approval=approval,
                execution_triggered=True,
                execution_mode="one_shot",
                execution_result_status="blocked" if "blocked" in str(exc).lower() else "failure",
                completion_marker_path=completion_marker_path,
                request_path=request_path,
                stopped_reason=str(exc),
                started_at=started_at,
                finished_at=_now(),
            )
            self._write_runtime(result)
            return result
        completion_marker_path = self._completion_marker_path()
        stopped_reason = "completion_marker_written" if completion_marker_path else "execution_completed"
        result = self._result(
            allow=True,
            handoff=handoff,
            approval=approval,
            execution_triggered=True,
            execution_mode="one_shot",
            execution_result_status="success",
            completion_marker_path=completion_marker_path,
            request_path=request_path,
            stopped_reason=stopped_reason,
            started_at=started_at,
            finished_at=_now(),
        )
        self._write_runtime(result)
        return result

    def _run_business_agent(
        self,
        handoff: dict[str, Any],
        approval: dict[str, Any],
        request_path: str | None,
        started_at: str,
    ) -> ApprovedAutonomousExecutionResult:
        business_id = str(handoff["business_id"])
        role_id = str(handoff["role_id"])
        task_id = str(handoff.get("task_id") or "")
        task_description = str(handoff.get("task_description") or "")
        adapter = BusinessAgentExecutionAdapter(self.base_path)
        try:
            outcome = adapter.run(
                business_id=business_id,
                role_id=role_id,
                task_id=task_id,
                task_description=task_description,
                approval_flag=True,
                dry_run=False,
            )
        except Exception as exc:  # bounded one-shot wrapper; stop safely on any failure, mirrors LocalExecutionAdapter's posture
            result = self._result(
                allow=True,
                handoff=handoff,
                approval=approval,
                execution_triggered=True,
                execution_mode="one_shot",
                execution_result_status="failure",
                completion_marker_path=None,
                request_path=request_path,
                stopped_reason=str(exc),
                started_at=started_at,
                finished_at=_now(),
            )
            self._write_runtime(result)
            return result
        result = self._result(
            allow=True,
            handoff=handoff,
            approval=approval,
            execution_triggered=True,
            execution_mode="one_shot",
            execution_result_status="success" if outcome.success else "failure",
            completion_marker_path=outcome.artifact_path,
            request_path=request_path,
            stopped_reason="completion_marker_written" if outcome.success else f"exit_code={outcome.exit_code}",
            started_at=started_at,
            finished_at=_now(),
        )
        self._write_runtime(result)
        return result

    def _request_path(self) -> str | None:
        path = self.base_path / "system" / "runtime" / "request" / "execution_request.json"
        return str(path) if path.exists() else None

    def _completion_marker_path(self) -> str | None:
        candidates = [
            self.base_path / "system" / "runtime" / "handoff" / "completion" / "latest.json",
            self.base_path / "system" / "runtime" / "completion" / "completion_report.json",
        ]
        for path in candidates:
            if path.exists():
                return str(path)
        return None

    def _result(
        self,
        *,
        allow: bool,
        handoff: dict[str, Any],
        approval: dict[str, Any],
        execution_triggered: bool,
        execution_mode: str,
        execution_result_status: str,
        completion_marker_path: str | None,
        request_path: str | None,
        stopped_reason: str,
        started_at: str,
        finished_at: str,
    ) -> ApprovedAutonomousExecutionResult:
        return ApprovedAutonomousExecutionResult(
            allow=allow,
            handoff_id=str(handoff.get("request_id")) if handoff else None,
            approval_id=str(approval.get("approval_id")) if approval else None,
            scope_type=str(approval.get("scope_type")) if approval else None,
            scope_id=str(approval.get("scope_id")) if approval else None,
            execution_triggered=execution_triggered,
            execution_mode=execution_mode,
            execution_result_status=execution_result_status,
            completion_marker_path=completion_marker_path,
            request_path=request_path,
            stopped_reason=stopped_reason,
            started_at=started_at,
            finished_at=finished_at,
        )

    def _write_runtime(self, result: ApprovedAutonomousExecutionResult) -> None:
        runtime_dir = self.base_path / "system" / "runtime" / "agent_execution"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        archive_dir = runtime_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "allow": result.allow,
            "handoff_id": result.handoff_id,
            "approval_id": result.approval_id,
            "scope_type": result.scope_type,
            "scope_id": result.scope_id,
            "execution_triggered": result.execution_triggered,
            "execution_mode": result.execution_mode,
            "execution_result_status": result.execution_result_status,
            "completion_marker_path": result.completion_marker_path,
            "request_path": result.request_path,
            "stopped_reason": result.stopped_reason,
            "started_at": result.started_at,
            "finished_at": result.finished_at,
        }
        (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (runtime_dir / "latest.md").write_text(_markdown(payload), encoding="utf-8")
        archive_key = f"execution_{result.started_at.replace(':', '').replace('-', '').replace('+', '').replace('.', '')}.json"
        (archive_dir / archive_key).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# APPROVED_AUTONOMOUS_EXECUTION",
            "",
            f"handoff_id: {payload.get('handoff_id') or ''}",
            f"allow: {str(bool(payload.get('allow'))).lower()}",
            f"approval_id: {payload.get('approval_id') or ''}",
            f"scope_type: {payload.get('scope_type') or ''}",
            f"scope_id: {payload.get('scope_id') or ''}",
            f"execution_triggered: {str(bool(payload.get('execution_triggered'))).lower()}",
            f"execution_mode: {payload.get('execution_mode') or ''}",
            f"execution_result_status: {payload.get('execution_result_status') or ''}",
            f"completion_marker_path: {payload.get('completion_marker_path') or ''}",
            f"request_path: {payload.get('request_path') or ''}",
            f"stopped_reason: {payload.get('stopped_reason') or ''}",
            f"started_at: {payload.get('started_at') or ''}",
            f"finished_at: {payload.get('finished_at') or ''}",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
