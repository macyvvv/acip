from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system.core.agent_execution_approval import evaluate_execution_approval
from system.orchestrator.execution_request import ExecutionRequestBuilder, ExecutionRequest


@dataclass(frozen=True)
class ApprovedHandoffExecutionBridgeResult:
    handoff_id: str | None
    approval_id: str | None
    allow: bool
    scope_type: str | None
    scope_id: str | None
    bridge_status: str
    execution_request_path: str | None
    denied_reason: str | None
    evaluated_at: str


class ApprovedHandoffExecutionBridgeError(ValueError):
    pass


class ApprovedHandoffExecutionBridge:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self) -> ApprovedHandoffExecutionBridgeResult:
        approval_result = evaluate_execution_approval(self.base_path)
        handoff = approval_result.handoff or {}
        approval = approval_result.approval or {}
        evaluated_at = _now()
        if not approval_result.allowed:
            self._write_bridge_artifact(
                {
                    "handoff_id": handoff.get("request_id"),
                    "approval_id": approval.get("approval_id"),
                    "allow": False,
                    "scope_type": approval.get("scope_type") or _handoff_scope_type(handoff),
                    "scope_id": approval.get("scope_id") or _handoff_scope_id(handoff),
                    "bridge_status": "denied",
                    "execution_request_path": None,
                    "denied_reason": approval_result.reason,
                    "evaluated_at": evaluated_at,
                }
            )
            return ApprovedHandoffExecutionBridgeResult(
                handoff_id=str(handoff.get("request_id")) if handoff else None,
                approval_id=str(approval.get("approval_id")) if approval else None,
                allow=False,
                scope_type=str(approval.get("scope_type")) if approval else None,
                scope_id=str(approval.get("scope_id")) if approval else None,
                bridge_status="denied",
                execution_request_path=None,
                denied_reason=approval_result.reason,
                evaluated_at=evaluated_at,
            )

        request_path = self._write_execution_request(handoff)
        self._write_bridge_artifact(
            {
                "handoff_id": handoff.get("request_id"),
                "approval_id": approval.get("approval_id"),
                "allow": True,
                "scope_type": approval.get("scope_type") or _handoff_scope_type(handoff),
                "scope_id": approval.get("scope_id") or _handoff_scope_id(handoff),
                "bridge_status": "allowed",
                "execution_request_path": str(request_path),
                "denied_reason": None,
                "evaluated_at": evaluated_at,
            }
        )
        return ApprovedHandoffExecutionBridgeResult(
            handoff_id=str(handoff.get("request_id")),
            approval_id=str(approval.get("approval_id")),
            allow=True,
            scope_type=str(approval.get("scope_type")),
            scope_id=str(approval.get("scope_id")),
            bridge_status="allowed",
            execution_request_path=str(request_path),
            denied_reason=None,
            evaluated_at=evaluated_at,
        )

    def _write_execution_request(self, handoff: dict[str, Any]) -> Path:
        builder = ExecutionRequestBuilder(self.base_path)
        request = ExecutionRequest(
            request_id=str(handoff.get("request_id")),
            request_status="ready",
            request_priority=100,
            approval_required=False,
            dependency=(
                "system/runtime/agent_handoff/latest.json",
                "system/runtime/agent_handoff/latest.md",
                "system/runtime/agent_handoff/approval.json",
                "system/runtime/agent_handoff/approval.md",
                "system/runtime/agent_state/latest.json",
            ),
            worker_assignment="Codex",
        )
        builder.write_runtime_request(request)
        canonical_runtime_dir = self.base_path / "system" / "runtime" / "request"
        canonical_runtime_dir.mkdir(parents=True, exist_ok=True)
        canonical_payload = {
            "request_id": request.request_id,
            "request_status": request.request_status,
            "request_priority": request.request_priority,
            "approval_required": request.approval_required,
            "dependency": list(request.dependency),
            "worker_assignment": request.worker_assignment,
            "next_action": handoff.get("next_action", ""),
            "objective": handoff.get("issue_title", ""),
            "issue_scope": handoff.get("issue_scope"),
            "issue_number": handoff.get("issue_number"),
            "approved_draft_id": handoff.get("approved_draft_id"),
        }
        canonical_request_path = canonical_runtime_dir / "execution_request.json"
        canonical_request_path.write_text(json.dumps(canonical_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (canonical_runtime_dir / "EXECUTION_REQUEST.md").write_text(
            "\n".join(
                [
                    "# EXECUTION_REQUEST",
                    "",
                    f"request_id: {request.request_id}",
                    f"request_status: {request.request_status}",
                    f"request_priority: {request.request_priority}",
                    f"approval_required: {str(request.approval_required).lower()}",
                    f"worker_assignment: {request.worker_assignment or 'null'}",
                    f"next_action: {handoff.get('next_action', '')}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return canonical_request_path

    def _write_bridge_artifact(self, payload: dict[str, Any]) -> None:
        runtime_dir = self.base_path / "system" / "runtime" / "agent_handoff"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        path = runtime_dir / "execution_bridge.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (runtime_dir / "execution_bridge.md").write_text(_bridge_markdown(payload), encoding="utf-8")


def _handoff_scope_type(handoff: dict[str, Any]) -> str:
    return "approved_draft" if handoff.get("approved_draft_id") else "issue"


def _handoff_scope_id(handoff: dict[str, Any]) -> str:
    if handoff.get("approved_draft_id"):
        return str(handoff.get("approved_draft_id"))
    return str(handoff.get("issue_number") or "")


def _bridge_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# APPROVED_HANDOFF_EXECUTION_BRIDGE",
            "",
            f"handoff_id: {payload.get('handoff_id') or ''}",
            f"approval_id: {payload.get('approval_id') or ''}",
            f"allow: {str(bool(payload.get('allow'))).lower()}",
            f"scope_type: {payload.get('scope_type') or ''}",
            f"scope_id: {payload.get('scope_id') or ''}",
            f"bridge_status: {payload.get('bridge_status') or ''}",
            f"execution_request_path: {payload.get('execution_request_path') or ''}",
            f"denied_reason: {payload.get('denied_reason') or ''}",
            f"evaluated_at: {payload.get('evaluated_at') or ''}",
            "",
        ]
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
