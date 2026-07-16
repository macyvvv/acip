from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from system.core.agent_role_registry import get_role

_ELIGIBLE_ROLE_KINDS = frozenset({"claude_invocation", "data_fetch"})
_MUTATING_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "Bash", "NotebookEdit"})
_REQUIRED_FIELDS = (
    "policy_id",
    "business_id",
    "role_id",
    "enabled",
    "max_auto_approvals_per_day",
    "max_allowed_tools",
    "max_model_capability",
    "authored_by",
    "authored_at",
    "reason",
)
_MODEL_CAPABILITY_ORDER = {
    "cost_optimized": 1,
    "reasoning": 2,
}


class ExecutionPreApprovalPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class ExecutionPreApprovalPolicyRecord:
    policy_id: str
    business_id: str
    role_id: str
    enabled: bool
    max_auto_approvals_per_day: int
    max_auto_approvals_per_week: int | None
    max_allowed_tools: int
    max_model_capability: str
    authored_by: str
    authored_at: str
    reason: str


def _policy_path(base_path: str | Path = ".") -> Path:
    root = Path(base_path)
    platform_path = root / "platform/system/runtime/agent_handoff/auto_approval_policy.json"
    if platform_path.exists():
        return platform_path
    system_path = root / "system/runtime/agent_handoff/auto_approval_policy.json"
    if system_path.exists():
        return system_path
    return platform_path


def _validate_structure(raw: dict) -> None:
    missing = [field for field in _REQUIRED_FIELDS if field not in raw]
    if missing:
        raise ExecutionPreApprovalPolicyError(f"Policy entry missing required field(s): {', '.join(missing)}")

    max_auto_approvals_per_day = raw["max_auto_approvals_per_day"]
    if not isinstance(max_auto_approvals_per_day, int) or max_auto_approvals_per_day <= 0:
        raise ExecutionPreApprovalPolicyError("max_auto_approvals_per_day must be a positive integer")

    max_auto_approvals_per_week = raw.get("max_auto_approvals_per_week")
    if max_auto_approvals_per_week is not None and (
        not isinstance(max_auto_approvals_per_week, int) or max_auto_approvals_per_week <= 0
    ):
        raise ExecutionPreApprovalPolicyError("max_auto_approvals_per_week must be a positive integer when present")

    max_allowed_tools = raw["max_allowed_tools"]
    if not isinstance(max_allowed_tools, int) or max_allowed_tools < 0:
        raise ExecutionPreApprovalPolicyError("max_allowed_tools must be a non-negative integer")

    max_model_capability = raw["max_model_capability"]
    if max_model_capability not in _MODEL_CAPABILITY_ORDER:
        raise ExecutionPreApprovalPolicyError(
            "max_model_capability must be one of "
            f"{sorted(_MODEL_CAPABILITY_ORDER)}"
        )


def _validate_role_eligibility(record: ExecutionPreApprovalPolicyRecord, base_path: str | Path) -> None:
    """Checked against the LIVE role registry, every time -- never cached or
    trusted from the policy file. Two independent load-bearing checks, both
    re-validated on every evaluation so a future registry change (a new
    pluggable_provider role, or a mutating tool added to an existing
    claude_invocation role's allowed_tools) is caught immediately rather than
    only at policy-authoring time:
      1. role_kind must be claude_invocation or data_fetch -- never
         pluggable_provider, which costs real money.
      2. allowed_tools must contain no mutating tool -- role_kind alone
         doesn't guarantee "safe to run unattended," since a future PR could
         add Write/Edit/Bash to an existing claude_invocation role without
         ever touching role_kind.
    Raises loudly (not a quiet None) -- a policy naming a now-dangerous or
    unknown role is a misconfiguration worth surfacing every time, not
    silently skipping."""
    role = get_role(record.role_id, base_path)
    if role is None:
        raise ExecutionPreApprovalPolicyError(f"Policy names unknown role_id '{record.role_id}'")
    if role.role_kind not in _ELIGIBLE_ROLE_KINDS:
        raise ExecutionPreApprovalPolicyError(
            f"Policy names role_id '{record.role_id}' with role_kind='{role.role_kind}' -- "
            f"only {sorted(_ELIGIBLE_ROLE_KINDS)} may ever be pre-approved, never pluggable_provider"
        )
    mutating = sorted(set(role.allowed_tools) & _MUTATING_TOOLS)
    if mutating:
        raise ExecutionPreApprovalPolicyError(
            f"Policy names role_id '{record.role_id}' whose allowed_tools include mutating tool(s) {mutating} -- "
            f"pre-approval requires a read-only tool surface"
        )
    if len(role.allowed_tools) > record.max_allowed_tools:
        raise ExecutionPreApprovalPolicyError(
            f"Policy names role_id '{record.role_id}' with {len(role.allowed_tools)} allowed_tools "
            f"but policy cap is {record.max_allowed_tools}"
        )
    role_capability_rank = _MODEL_CAPABILITY_ORDER.get(role.model_capability)
    policy_capability_rank = _MODEL_CAPABILITY_ORDER[record.max_model_capability]
    if role_capability_rank is None:
        raise ExecutionPreApprovalPolicyError(
            f"Policy names role_id '{record.role_id}' with unknown model_capability '{role.model_capability}'"
        )
    if role_capability_rank > policy_capability_rank:
        raise ExecutionPreApprovalPolicyError(
            f"Policy names role_id '{record.role_id}' with model_capability='{role.model_capability}' "
            f"but policy cap is '{record.max_model_capability}'"
        )


def _to_record(raw: dict) -> ExecutionPreApprovalPolicyRecord:
    return ExecutionPreApprovalPolicyRecord(
        policy_id=str(raw["policy_id"]),
        business_id=str(raw["business_id"]),
        role_id=str(raw["role_id"]),
        enabled=bool(raw["enabled"]),
        max_auto_approvals_per_day=raw["max_auto_approvals_per_day"],
        max_auto_approvals_per_week=raw.get("max_auto_approvals_per_week"),
        max_allowed_tools=raw["max_allowed_tools"],
        max_model_capability=str(raw["max_model_capability"]),
        authored_by=str(raw["authored_by"]),
        authored_at=str(raw["authored_at"]),
        reason=str(raw["reason"]),
    )


def load_execution_pre_approval_policies(base_path: str | Path = ".") -> list[ExecutionPreApprovalPolicyRecord]:
    path = _policy_path(base_path)
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ExecutionPreApprovalPolicyError(f"{path} is not valid JSON: {exc}") from exc
    records = []
    for entry in raw.get("policies", []):
        _validate_structure(entry)
        records.append(_to_record(entry))
    return records


def get_execution_pre_approval_policy(
    business_id: str, role_id: str, base_path: str | Path = "."
) -> ExecutionPreApprovalPolicyRecord | None:
    """None on missing file, missing entry, or a disabled entry -- absence
    always means "not authorized," fail closed. A malformed entry for a
    DIFFERENT (business_id, role_id) still raises at load time (a broken
    policy file is itself worth surfacing), but this function never returns
    anything permissive by default. For the matching entry specifically, the
    role-eligibility check (role_kind + allowed_tools, against the live
    registry) is re-run on every call and raises loudly if it fails, even
    when enabled=true in the file."""
    for record in load_execution_pre_approval_policies(base_path):
        if record.business_id == business_id and record.role_id == role_id:
            if not record.enabled:
                return None
            _validate_role_eligibility(record, base_path)
            return record
    return None
