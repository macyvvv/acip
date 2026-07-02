from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from system.core.path_resolver import get_repo_root


@dataclass(frozen=True)
class ExecutionApprovalResult:
    allowed: bool
    reason: str
    approval: dict[str, Any] | None
    handoff: dict[str, Any] | None


class AgentExecutionApprovalError(ValueError):
    pass


def load_latest_handoff(base_path: str | Path = ".") -> dict[str, Any] | None:
    path = Path(base_path) / "system" / "runtime" / "agent_handoff" / "latest.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def load_approval_artifact(base_path: str | Path = ".") -> dict[str, Any] | None:
    path = Path(base_path) / "system" / "runtime" / "agent_handoff" / "approval.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def evaluate_execution_approval(base_path: str | Path = ".") -> ExecutionApprovalResult:
    handoff = load_latest_handoff(base_path)
    approval = load_approval_artifact(base_path)
    if handoff is None:
        return ExecutionApprovalResult(False, "missing_handoff", None, None)
    if approval is None:
        return ExecutionApprovalResult(False, "missing_approval", None, handoff)

    required_fields = (
        "approval_id",
        "handoff_id",
        "scope_type",
        "scope_id",
        "decision_status",
        "approved_by",
        "approved_at",
        "reason",
        "execution_enabled",
        "supersedes",
    )
    missing = [field for field in required_fields if field not in approval]
    if missing:
        return ExecutionApprovalResult(False, f"invalid_approval_missing:{','.join(missing)}", approval, handoff)

    if str(approval.get("decision_status")) != "approved":
        return ExecutionApprovalResult(False, f"decision_status={approval.get('decision_status')}", approval, handoff)
    if not bool(approval.get("execution_enabled", False)):
        return ExecutionApprovalResult(False, "execution_disabled", approval, handoff)
    if approval.get("supersedes"):
        return ExecutionApprovalResult(False, "approval_superseded", approval, handoff)
    if str(approval.get("handoff_id")) != str(handoff.get("request_id")):
        return ExecutionApprovalResult(False, "handoff_mismatch", approval, handoff)
    if str(approval.get("scope_type")) != _handoff_scope_type(handoff):
        return ExecutionApprovalResult(False, "scope_type_mismatch", approval, handoff)
    if str(approval.get("scope_id")) != _handoff_scope_id(handoff):
        return ExecutionApprovalResult(False, "scope_id_mismatch", approval, handoff)
    return ExecutionApprovalResult(True, "approved", approval, handoff)


def _handoff_scope_type(handoff: dict[str, Any]) -> str:
    return "approved_draft" if handoff.get("approved_draft_id") else "issue"


def _handoff_scope_id(handoff: dict[str, Any]) -> str:
    if handoff.get("approved_draft_id"):
        return str(handoff.get("approved_draft_id"))
    return str(handoff.get("issue_number") or "")
