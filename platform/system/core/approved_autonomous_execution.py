from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from system.core.agent_execution_approval import evaluate_business_agent_scope_approval, evaluate_execution_approval
from system.core.business_agent_handoff import scope_dir
from system.core.business_agent_task_queue import mark_task_status
from system.core.business_agent_trigger import evaluate_and_enqueue_next_tasks
from system.core.execution_pre_approval_control import is_pre_approval_paused
from system.core.execution_pre_approval_policy import (
    ExecutionPreApprovalPolicyError,
    get_execution_pre_approval_policy,
)
from system.core.execution_pre_approval_state import (
    ExecutionPreApprovalAlreadyInFlightError,
    ExecutionPreApprovalCapExceededError,
    claim_pre_approval,
    mark_pre_approval_outcome,
)
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
    authorization_source: str = "human_approval"
    policy_id: str | None = None


class ApprovedAutonomousExecutionError(ValueError):
    pass


class ApprovedAutonomousExecution:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(
        self,
        *,
        business_id: str | None = None,
        role_id: str | None = None,
        task_id: str | None = None,
    ) -> ApprovedAutonomousExecutionResult:
        started_at = _now()
        scope_requested = bool(business_id and role_id and task_id)
        if scope_requested:
            approval_result = evaluate_business_agent_scope_approval(business_id, role_id, task_id, self.base_path)
        else:
            approval_result = evaluate_execution_approval(self.base_path)
        handoff = approval_result.handoff or {}
        approval = approval_result.approval or {}
        if not approval_result.allowed:
            if scope_requested and approval_result.reason == "missing_approval":
                pre_approved = self._try_policy_pre_approval(
                    business_id, role_id, task_id, handoff, self._request_path(), started_at
                )
                if pre_approved is not None:
                    return pre_approved
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
            self._write_runtime(result, handoff)
            return result

        request_path = self._request_path()
        if scope_requested or (handoff.get("business_id") and handoff.get("role_id")):
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
            self._write_runtime(result, handoff)
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
        self._write_runtime(result, handoff)
        return result

    def _run_business_agent(
        self,
        handoff: dict[str, Any],
        approval: dict[str, Any],
        request_path: str | None,
        started_at: str,
        *,
        authorization_source: str = "human_approval",
        policy_id: str | None = None,
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
                authorization_source=authorization_source,
                policy_id=policy_id,
            )
            self._write_runtime(result, handoff)
            if authorization_source == "policy_pre_approval":
                mark_pre_approval_outcome(business_id, role_id, task_id, False, self.base_path)
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
            stopped_reason=(
                "completion_marker_written"
                if outcome.success
                else (getattr(outcome, "failure_reason", None) or f"exit_code={outcome.exit_code}")
            ),
            started_at=started_at,
            finished_at=_now(),
            authorization_source=authorization_source,
            policy_id=policy_id,
        )
        self._write_runtime(result, handoff)
        if authorization_source == "policy_pre_approval":
            mark_pre_approval_outcome(business_id, role_id, task_id, outcome.success, self.base_path)
            if outcome.success:
                # Level 3a's entire premise is that no one is expected to go
                # through the Approval Console for these scopes -- unlike the
                # human-approved path (which relies on the console calling
                # this itself), nothing else will ever flip this queue entry
                # out of "candidate" otherwise, silently misrepresenting an
                # already-executed task as still awaiting operator selection.
                mark_task_status(business_id, role_id, task_id, "completed", self.base_path)
        if outcome.success:
            # Level 1 queue-population automation only -- this can enqueue and
            # possibly activate the next candidate, it never approves or runs
            # anything. See docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md.
            evaluate_and_enqueue_next_tasks(business_id, role_id, task_id, outcome.artifact_path, self.base_path)
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
        authorization_source: str = "human_approval",
        policy_id: str | None = None,
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
            authorization_source=authorization_source,
            policy_id=policy_id,
        )

    def _try_policy_pre_approval(
        self,
        business_id: str,
        role_id: str,
        task_id: str,
        handoff: dict[str, Any],
        request_path: str | None,
        started_at: str,
    ) -> ApprovedAutonomousExecutionResult | None:
        """Level 3a: policy-based pre-approval of the execution DECISION.
        Returns None if no enabled, eligible policy applies -- caller then
        falls through to the original missing_approval denial, unchanged.
        Only ever invoked when approval_result.reason == "missing_approval"
        (checked by the caller) -- an approval.json that exists but doesn't
        match (rejected/superseded/mismatched) reaches this method exactly
        never, enforced structurally by the caller, not by anything here.

        Never synthesizes an approval.json -- decision_status: approved
        stays exclusively human-written, for every scope, forever. This is
        a wholly separate authorization path."""
        if is_pre_approval_paused(self.base_path):
            return self._result(
                allow=False,
                handoff=handoff,
                approval={},
                execution_triggered=False,
                execution_mode="denied",
                execution_result_status="denied",
                completion_marker_path=None,
                request_path=request_path,
                stopped_reason="pre_approval_paused",
                started_at=started_at,
                finished_at=_now(),
            )

        try:
            policy = get_execution_pre_approval_policy(business_id, role_id, self.base_path)
        except ExecutionPreApprovalPolicyError as exc:
            # Fail closed AND fail loud: a misconfigured policy (e.g. naming a
            # now-dangerous role) must never silently "proceed anyway," and
            # must still leave an audit trail -- never let this propagate as
            # an uncaught exception, which would lose both.
            result = self._result(
                allow=False,
                handoff=handoff,
                approval={},
                execution_triggered=False,
                execution_mode="denied",
                execution_result_status="denied",
                completion_marker_path=None,
                request_path=request_path,
                stopped_reason=f"pre_approval_policy_error:{exc}",
                started_at=started_at,
                finished_at=_now(),
            )
            self._write_runtime(result, handoff)
            return result

        if policy is None:
            return None

        # Secondary, defense-in-depth check, for one specific recovery case
        # only (the pre-approval state shard was reset/never written but a
        # real completed execution already exists on disk) -- NOT relied on
        # for concurrency correctness, which is entirely the state module's
        # job. Checked before claiming, so a recovery case never consumes a
        # cap slot for work that already happened.
        artifact_path = self.base_path / "system" / "runtime" / "business_agents" / business_id / role_id / task_id / "latest.json"
        if artifact_path.exists():
            try:
                already_succeeded = bool(json.loads(artifact_path.read_text(encoding="utf-8")).get("success"))
            except json.JSONDecodeError:
                already_succeeded = False
            if already_succeeded:
                result = self._result(
                    allow=True,
                    handoff=handoff,
                    approval={},
                    execution_triggered=False,
                    execution_mode="skipped_duplicate",
                    execution_result_status="already_executed",
                    completion_marker_path=str(artifact_path),
                    request_path=request_path,
                    stopped_reason="duplicate_pre_approval_skipped_already_succeeded",
                    started_at=started_at,
                    finished_at=_now(),
                    authorization_source="policy_pre_approval",
                    policy_id=policy.policy_id,
                )
                self._write_runtime(result, handoff)
                mark_task_status(business_id, role_id, task_id, "completed", self.base_path)
                return result

        try:
            claim = claim_pre_approval(
                business_id,
                role_id,
                task_id,
                policy.policy_id,
                policy.max_auto_approvals_per_day,
                policy.max_auto_approvals_per_week,
                self.base_path,
            )
        except ExecutionPreApprovalCapExceededError as exc:
            result = self._result(
                allow=False,
                handoff=handoff,
                approval={},
                execution_triggered=False,
                execution_mode="denied",
                execution_result_status="denied",
                completion_marker_path=None,
                request_path=request_path,
                stopped_reason=f"pre_approval_cap_exceeded:{exc}",
                started_at=started_at,
                finished_at=_now(),
            )
            self._write_runtime(result, handoff)
            return result
        except ExecutionPreApprovalAlreadyInFlightError as exc:
            result = self._result(
                allow=False,
                handoff=handoff,
                approval={},
                execution_triggered=False,
                execution_mode="denied",
                execution_result_status="denied",
                completion_marker_path=None,
                request_path=request_path,
                stopped_reason=f"pre_approval_already_in_flight:{exc}",
                started_at=started_at,
                finished_at=_now(),
            )
            self._write_runtime(result, handoff)
            return result

        if claim == "already_completed":
            result = self._result(
                allow=True,
                handoff=handoff,
                approval={},
                execution_triggered=False,
                execution_mode="skipped_duplicate",
                execution_result_status="already_executed",
                completion_marker_path=None,
                request_path=request_path,
                stopped_reason="duplicate_pre_approval_skipped_already_succeeded",
                started_at=started_at,
                finished_at=_now(),
                authorization_source="policy_pre_approval",
                policy_id=policy.policy_id,
            )
            self._write_runtime(result, handoff)
            mark_task_status(business_id, role_id, task_id, "completed", self.base_path)
            return result

        return self._run_business_agent(
            handoff,
            {},
            request_path,
            started_at,
            authorization_source="policy_pre_approval",
            policy_id=policy.policy_id,
        )

    def _write_runtime(self, result: ApprovedAutonomousExecutionResult, handoff: dict[str, Any] | None = None) -> None:
        handoff = handoff or {}
        if handoff.get("business_id") and handoff.get("role_id"):
            # Per-scope result storage (Level 2): a shared top-level
            # agent_execution/latest.json would let two businesses executing
            # around the same moment clobber each other's result.
            runtime_dir = (
                self.base_path
                / "system"
                / "runtime"
                / "agent_execution"
                / "scopes"
                / str(handoff["business_id"])
                / str(handoff["role_id"])
                / str(handoff.get("task_id") or "")
            )
        else:
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
            "authorization_source": result.authorization_source,
            "policy_id": result.policy_id,
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
            f"authorization_source: {payload.get('authorization_source') or ''}",
            f"policy_id: {payload.get('policy_id') or ''}",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
