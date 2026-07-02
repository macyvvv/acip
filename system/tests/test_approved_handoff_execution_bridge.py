from __future__ import annotations

import json
from pathlib import Path

from system.core.approved_handoff_execution_bridge import ApprovedHandoffExecutionBridge


def _write_handoff(path: Path, *, request_id: str = "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001", scope_id: str = "DRAFT-OPP-KABUKICHO-001") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "issue_scope": "draft:DRAFT-OPP-KABUKICHO-001",
                "issue_number": None,
                "approved_draft_id": scope_id,
                "issue_title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                "thread_id": "THREAD-DRAFT-DRAFT-OPP-KABUKICHO-001",
                "thread_final_state": "waiting_for_review",
                "stop_reason": "idle",
                "request_id": request_id,
                "request_path": "system/runtime/request/execution_request.json",
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
        "decision_status": "approved",
        "approved_by": "Human",
        "approved_at": "2026-07-02T12:00:00+00:00",
        "reason": "Approved for bounded execution bridge",
        "execution_enabled": True,
        "supersedes": None,
    }
    payload.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def test_missing_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")

    result = ApprovedHandoffExecutionBridge(tmp_path).run()

    assert result.allow is False
    assert result.execution_request_path is None
    assert (tmp_path / "system" / "runtime" / "agent_handoff" / "execution_bridge.json").exists()


def test_pending_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        decision_status="pending",
        execution_enabled=False,
    )

    result = ApprovedHandoffExecutionBridge(tmp_path).run()

    assert result.allow is False
    assert result.denied_reason == "decision_status=pending"


def test_rejected_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        decision_status="rejected",
        execution_enabled=False,
    )

    result = ApprovedHandoffExecutionBridge(tmp_path).run()

    assert result.allow is False
    assert result.denied_reason == "decision_status=rejected"


def test_approved_matching_approval_bridged(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json")

    result = ApprovedHandoffExecutionBridge(tmp_path).run()

    assert result.allow is True
    assert result.execution_request_path.endswith("system/runtime/request/execution_request.json")
    assert (tmp_path / "system" / "runtime" / "request" / "execution_request.json").exists()
    assert (tmp_path / "system" / "runtime" / "agent_handoff" / "execution_bridge.json").exists()


def test_mismatched_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        scope_id="DRAFT-OTHER",
    )

    result = ApprovedHandoffExecutionBridge(tmp_path).run()

    assert result.allow is False
    assert result.denied_reason == "scope_id_mismatch"


def test_superseded_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        supersedes="APP-OLD",
    )

    result = ApprovedHandoffExecutionBridge(tmp_path).run()

    assert result.allow is False
    assert result.denied_reason == "approval_superseded"


def test_no_hidden_mutation_occurs(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json")
    before = (tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json").read_text(encoding="utf-8")

    ApprovedHandoffExecutionBridge(tmp_path).run()

    after = (tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json").read_text(encoding="utf-8")
    assert before == after
