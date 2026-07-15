from __future__ import annotations

import json
from pathlib import Path

from system.core.agent_execution_approval import evaluate_business_agent_scope_approval, evaluate_execution_approval
from system.core.business_agent_handoff import write_business_agent_handoff, scope_dir


def _write_handoff(path: Path, *, request_id: str = "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001", scope_type: str = "approved_draft", scope_id: str = "DRAFT-OPP-KABUKICHO-001") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "issue_scope": "draft:DRAFT-OPP-KABUKICHO-001",
                "issue_number": None,
                "approved_draft_id": scope_id if scope_type == "approved_draft" else None,
                "issue_title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                "thread_id": "THREAD-DRAFT-DRAFT-OPP-KABUKICHO-001",
                "thread_final_state": "waiting_for_review",
                "stop_reason": "idle",
                "request_id": request_id,
                "request_path": "platform/system/runtime/request/execution_request.json",
                "next_action": "Review the handoff and, if approved, continue through existing execution flow.",
                "created_at": "2026-07-02T05:29:29.642877+00:00",
                "source": "agent_issue_bridge",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_approval(path: Path, **overrides) -> None:
    payload = {
        "approval_id": "APP-AGENT-HANDOFF-0001",
        "handoff_id": "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
        "scope_type": "approved_draft",
        "scope_id": "DRAFT-OPP-KABUKICHO-001",
        "decision_status": "pending",
        "approved_by": None,
        "approved_at": None,
        "reason": "",
        "execution_enabled": False,
        "supersedes": None,
    }
    payload.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def test_missing_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is False
    assert result.reason == "missing_approval"


def test_pending_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json")

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is False
    assert "decision_status=pending" == result.reason


def test_rejected_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        decision_status="rejected",
        execution_enabled=False,
    )

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is False
    assert result.reason == "decision_status=rejected"


def test_approved_matching_handoff_allowed(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        decision_status="approved",
        approved_by="Human",
        approved_at="2026-07-02T10:00:00+00:00",
        reason="Approved for bounded execution",
        execution_enabled=True,
    )

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is True
    assert result.reason == "approved"


def test_stale_superseded_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        decision_status="approved",
        approved_by="Human",
        approved_at="2026-07-02T10:00:00+00:00",
        reason="Superseded approval",
        execution_enabled=True,
        supersedes="APP-OLD",
    )

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is False
    assert result.reason == "approval_superseded"


def _write_business_role_handoff(path: Path, *, business_id: str = "text_syndicate", role_id: str = "market_research", task_id: str = "task-0001", request_id: str = "REQ-TEXT-SYNDICATE-MARKET-RESEARCH-0001") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "business_id": business_id,
                "role_id": role_id,
                "task_id": task_id,
                "issue_number": None,
                "approved_draft_id": None,
                "request_id": request_id,
                "created_at": "2026-07-07T00:00:00+00:00",
                "source": "business_agent_handoff",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_business_role_task_scope_approved_when_matching(tmp_path: Path) -> None:
    _write_business_role_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        handoff_id="REQ-TEXT-SYNDICATE-MARKET-RESEARCH-0001",
        scope_type="business_role_task",
        scope_id="text_syndicate:market_research:task-0001",
        decision_status="approved",
        approved_by="Human",
        approved_at="2026-07-07T00:00:00+00:00",
        reason="Pilot approval",
        execution_enabled=True,
    )

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is True
    assert result.reason == "approved"


def test_business_role_task_scope_mismatch_denied(tmp_path: Path) -> None:
    _write_business_role_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        handoff_id="REQ-TEXT-SYNDICATE-MARKET-RESEARCH-0001",
        scope_type="business_role_task",
        scope_id="text_syndicate:marketing:task-0001",  # wrong role_id
        decision_status="approved",
        approved_by="Human",
        approved_at="2026-07-07T00:00:00+00:00",
        reason="Pilot approval",
        execution_enabled=True,
    )

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is False
    assert result.reason == "scope_id_mismatch"


def test_existing_issue_scope_path_unaffected_by_business_role_discriminator(tmp_path: Path) -> None:
    # Existing issue/draft handoffs never set business_id/role_id, so the new
    # branch must be unreachable for them -- this is the backward-compat guarantee.
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        decision_status="approved",
        approved_by="Human",
        approved_at="2026-07-02T10:00:00+00:00",
        reason="Approved for bounded execution",
        execution_enabled=True,
    )

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is True
    assert result.approval["scope_type"] == "approved_draft"


def test_mismatched_scope_id_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        decision_status="approved",
        approved_by="Human",
        approved_at="2026-07-02T10:00:00+00:00",
        reason="Scope mismatch",
        execution_enabled=True,
        scope_id="DRAFT-OTHER",
    )

    result = evaluate_execution_approval(tmp_path)

    assert result.allowed is False
    assert result.reason == "scope_id_mismatch"


def _write_scope_approval(business_id: str, role_id: str, task_id: str, base_path: Path, **overrides) -> None:
    handoff_id = f"REQ-{business_id}-{role_id}-{task_id}".replace("_", "-").upper()
    payload = {
        "approval_id": "APP-1",
        "handoff_id": handoff_id,
        "scope_type": "business_role_task",
        "scope_id": f"{business_id}:{role_id}:{task_id}",
        "decision_status": "approved",
        "approved_by": "Human",
        "approved_at": "2026-07-10T00:00:00+00:00",
        "reason": "test",
        "execution_enabled": True,
        "supersedes": None,
    }
    payload.update(overrides)
    path = scope_dir(business_id, role_id, task_id, base_path) / "approval.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def test_business_agent_scope_approval_allows_matching_scope(tmp_path: Path) -> None:
    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc", tmp_path)
    _write_scope_approval("text_syndicate", "market_research", "task-0001", tmp_path)

    result = evaluate_business_agent_scope_approval("text_syndicate", "market_research", "task-0001", tmp_path)

    assert result.allowed is True


def test_business_agent_scope_approval_does_not_leak_across_scopes(tmp_path: Path) -> None:
    # The cross-scope forgery/leak test: business A has a valid, matching,
    # approved-and-pending approval; business B has a handoff but NO
    # approval at all. Approving A must never authorize executing B --
    # this is the exact failure mode the approval contract exists to
    # prevent, and the one a careless "share the validation logic" refactor
    # could introduce by accident (checking "is *some* approval approved"
    # instead of "is *this scope's* approval approved").
    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc A", tmp_path)
    _write_scope_approval("text_syndicate", "market_research", "task-0001", tmp_path)

    write_business_agent_handoff("kabukicho_survival_map", "marketing", "task-0007", "desc B", tmp_path)
    # deliberately no approval written for B

    result_a = evaluate_business_agent_scope_approval("text_syndicate", "market_research", "task-0001", tmp_path)
    result_b = evaluate_business_agent_scope_approval("kabukicho_survival_map", "marketing", "task-0007", tmp_path)

    assert result_a.allowed is True
    assert result_b.allowed is False
    assert result_b.reason == "missing_approval"


def test_business_agent_scope_approval_mismatched_scope_denied(tmp_path: Path) -> None:
    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc", tmp_path)
    # approval for a DIFFERENT task_id under the same business/role
    _write_scope_approval(
        "text_syndicate", "market_research", "task-0001", tmp_path,
        scope_id="text_syndicate:market_research:task-9999",
    )

    result = evaluate_business_agent_scope_approval("text_syndicate", "market_research", "task-0001", tmp_path)

    assert result.allowed is False
    assert result.reason == "scope_id_mismatch"


def test_business_agent_scope_approval_missing_handoff(tmp_path: Path) -> None:
    result = evaluate_business_agent_scope_approval("text_syndicate", "market_research", "task-0001", tmp_path)
    assert result.allowed is False
    assert result.reason == "missing_handoff"
