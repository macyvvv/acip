from __future__ import annotations

import json
from pathlib import Path

import pytest

from system.core.execution_pre_approval_policy import (
    ExecutionPreApprovalPolicyError,
    get_execution_pre_approval_policy,
    load_execution_pre_approval_policies,
)


def _write_policy(tmp_path: Path, policies: list[dict]) -> None:
    path = tmp_path / "system/runtime/agent_handoff/auto_approval_policy.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "policies": policies}))


def _entry(**overrides) -> dict:
    base = {
        "policy_id": "PREAPP-TEXT_SYNDICATE-MARKET_RESEARCH-0001",
        "business_id": "text_syndicate",
        "role_id": "market_research",
        "enabled": True,
        "max_auto_approvals_per_day": 1,
        "max_auto_approvals_per_week": 5,
        "authored_by": "macy",
        "authored_at": "2026-07-11T00:00:00+00:00",
        "reason": "pilot",
    }
    base.update(overrides)
    return base


def test_missing_file_returns_none(tmp_path: Path) -> None:
    assert get_execution_pre_approval_policy("text_syndicate", "market_research", tmp_path) is None
    assert load_execution_pre_approval_policies(tmp_path) == []


def test_well_formed_load_and_lookup(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry()])
    record = get_execution_pre_approval_policy("text_syndicate", "market_research", tmp_path)
    assert record is not None
    assert record.business_id == "text_syndicate"
    assert record.role_id == "market_research"
    assert record.max_auto_approvals_per_day == 1


def test_missing_entry_returns_none(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry()])
    assert get_execution_pre_approval_policy("text_syndicate", "marketing", tmp_path) is None
    assert get_execution_pre_approval_policy("kabukicho_survival_map", "market_research", tmp_path) is None


def test_disabled_entry_returns_none(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(enabled=False)])
    assert get_execution_pre_approval_policy("text_syndicate", "market_research", tmp_path) is None


def test_missing_required_field_raises(tmp_path: Path) -> None:
    entry = _entry()
    del entry["max_auto_approvals_per_day"]
    _write_policy(tmp_path, [entry])
    with pytest.raises(ExecutionPreApprovalPolicyError):
        load_execution_pre_approval_policies(tmp_path)


def test_non_positive_cap_raises(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(max_auto_approvals_per_day=0)])
    with pytest.raises(ExecutionPreApprovalPolicyError):
        load_execution_pre_approval_policies(tmp_path)


def test_unknown_role_id_raises(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(role_id="not_a_real_role")])
    with pytest.raises(ExecutionPreApprovalPolicyError):
        get_execution_pre_approval_policy("text_syndicate", "not_a_real_role", tmp_path)


def test_pluggable_provider_role_raises_even_if_enabled(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(role_id="image_generation", policy_id="PREAPP-X-IMAGE-0001")])
    with pytest.raises(ExecutionPreApprovalPolicyError):
        get_execution_pre_approval_policy("text_syndicate", "image_generation", tmp_path)

    _write_policy(tmp_path, [_entry(role_id="video_generation", policy_id="PREAPP-X-VIDEO-0001")])
    with pytest.raises(ExecutionPreApprovalPolicyError):
        get_execution_pre_approval_policy("text_syndicate", "video_generation", tmp_path)


def test_all_claude_invocation_and_data_fetch_roles_are_eligible(tmp_path: Path) -> None:
    for role_id in ("market_research", "marketing", "doc_creation", "scenario_writing", "pdca", "analytics"):
        _write_policy(tmp_path, [_entry(role_id=role_id, policy_id=f"PREAPP-{role_id}")])
        record = get_execution_pre_approval_policy("text_syndicate", role_id, tmp_path)
        assert record is not None, f"{role_id} should be eligible"


def test_mutating_allowed_tools_raises_even_for_claude_invocation(tmp_path: Path, monkeypatch) -> None:
    # No currently-seeded role actually has a mutating tool, so this exercises
    # the safety check directly against a stand-in role, confirming it fires
    # independently of the role_kind check (role_kind is claude_invocation
    # here -- only allowed_tools makes this ineligible).
    import system.core.execution_pre_approval_policy as module

    class _FakeRole:
        role_kind = "claude_invocation"
        allowed_tools = ("Read", "Bash")

    monkeypatch.setattr(module, "get_role", lambda role_id, base_path: _FakeRole())
    _write_policy(tmp_path, [_entry(role_id="marketing")])
    with pytest.raises(ExecutionPreApprovalPolicyError):
        get_execution_pre_approval_policy("text_syndicate", "marketing", tmp_path)


def test_cross_scope_isolation(tmp_path: Path) -> None:
    _write_policy(
        tmp_path,
        [
            _entry(policy_id="A", business_id="text_syndicate", role_id="market_research", max_auto_approvals_per_day=1),
            _entry(policy_id="B", business_id="kabukicho_survival_map", role_id="marketing", max_auto_approvals_per_day=3),
        ],
    )
    a = get_execution_pre_approval_policy("text_syndicate", "market_research", tmp_path)
    b = get_execution_pre_approval_policy("kabukicho_survival_map", "marketing", tmp_path)
    assert a.max_auto_approvals_per_day == 1
    assert b.max_auto_approvals_per_day == 3
    assert get_execution_pre_approval_policy("text_syndicate", "marketing", tmp_path) is None
