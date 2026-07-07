from __future__ import annotations

import json
from pathlib import Path

from system.core.approved_autonomous_execution import ApprovedAutonomousExecution


def _write_handoff(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "issue_scope": "draft:DRAFT-OPP-KABUKICHO-001",
                "issue_number": None,
                "approved_draft_id": "DRAFT-OPP-KABUKICHO-001",
                "issue_title": "Kabukicho Survival Map MVP expansion: validate next-value POI and distribution opportunities",
                "thread_id": "THREAD-DRAFT-DRAFT-OPP-KABUKICHO-001",
                "thread_final_state": "waiting_for_review",
                "stop_reason": "idle",
                "request_id": "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
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


def test_no_approval_denied(tmp_path: Path) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")

    result = ApprovedAutonomousExecution(tmp_path).run()

    assert result.execution_triggered is False
    assert result.execution_result_status == "denied"
    assert (tmp_path / "system" / "runtime" / "agent_execution" / "latest.json").exists()


def test_approved_handoff_executes_once(tmp_path: Path, monkeypatch) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json")

    calls: list[tuple[bool, bool]] = []

    def fake_run(self, *, approval_flag: bool = False, dry_run: bool = True):
        calls.append((approval_flag, dry_run))
        completion_dir = tmp_path / "system" / "runtime" / "completion"
        completion_dir.mkdir(parents=True, exist_ok=True)
        (completion_dir / "completion_report.json").write_text("{}", encoding="utf-8")
        return object()

    monkeypatch.setattr("system.core.approved_autonomous_execution.LocalExecutionAdapter.run", fake_run)

    result = ApprovedAutonomousExecution(tmp_path).run()

    assert calls == [(True, False)]
    assert result.execution_triggered is True
    assert result.execution_result_status == "success"
    assert result.completion_marker_path.endswith("completion_report.json")


def _write_business_role_handoff(path: Path, *, task_description: str = "Research impression-driving niches") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "business_id": "text_syndicate",
                "role_id": "market_research",
                "task_id": "task-0001",
                "task_description": task_description,
                "issue_number": None,
                "approved_draft_id": None,
                "request_id": "REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001",
                "created_at": "2026-07-07T00:00:00+00:00",
                "source": "business_agent_handoff",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_business_role_task_dispatches_to_business_agent_adapter(tmp_path: Path, monkeypatch) -> None:
    _write_business_role_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        handoff_id="REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001",
        scope_type="business_role_task",
        scope_id="text_syndicate:market_research:task-0001",
    )

    calls: list[dict] = []

    class FakeOutcome:
        success = True
        artifact_path = "system/runtime/business_agents/text_syndicate/market_research/task-0001/latest.json"
        exit_code = 0

    def fake_run(self, *, business_id, role_id, task_id, task_description="", approval_flag=False, dry_run=True):
        calls.append(
            {
                "business_id": business_id,
                "role_id": role_id,
                "task_id": task_id,
                "task_description": task_description,
                "approval_flag": approval_flag,
                "dry_run": dry_run,
            }
        )
        return FakeOutcome()

    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", fake_run)

    result = ApprovedAutonomousExecution(tmp_path).run()

    assert calls == [
        {
            "business_id": "text_syndicate",
            "role_id": "market_research",
            "task_id": "task-0001",
            "task_description": "Research impression-driving niches",
            "approval_flag": True,
            "dry_run": False,
        }
    ]
    assert result.execution_triggered is True
    assert result.execution_result_status == "success"
    assert result.completion_marker_path.endswith("market_research/task-0001/latest.json")


def test_business_role_task_failure_stops_safely(tmp_path: Path, monkeypatch) -> None:
    _write_business_role_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        handoff_id="REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001",
        scope_type="business_role_task",
        scope_id="text_syndicate:market_research:task-0001",
    )

    def fake_run(self, *, business_id, role_id, task_id, task_description="", approval_flag=False, dry_run=True):
        raise ValueError("business agent execution failed")

    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", fake_run)

    result = ApprovedAutonomousExecution(tmp_path).run()

    assert result.execution_triggered is True
    assert result.execution_result_status == "failure"
    assert "business agent execution failed" in result.stopped_reason


def test_issue_scope_path_still_uses_local_execution_adapter(tmp_path: Path, monkeypatch) -> None:
    # Existing issue/draft handoffs never set business_id/role_id -- confirms the
    # new branch doesn't leak into the existing repo-dev path.
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json")

    business_agent_calls: list[object] = []

    def fake_business_agent_run(self, **kwargs):
        business_agent_calls.append(kwargs)
        raise AssertionError("BusinessAgentExecutionAdapter should not be invoked for an issue-scoped handoff")

    def fake_local_run(self, *, approval_flag: bool = False, dry_run: bool = True):
        return object()

    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", fake_business_agent_run)
    monkeypatch.setattr("system.core.approved_autonomous_execution.LocalExecutionAdapter.run", fake_local_run)

    result = ApprovedAutonomousExecution(tmp_path).run()

    assert business_agent_calls == []
    assert result.execution_triggered is True
    assert result.execution_result_status == "success"


def test_blocked_result_stops_safely(tmp_path: Path, monkeypatch) -> None:
    _write_handoff(tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json")
    _write_approval(tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json")

    def fake_run(self, *, approval_flag: bool = False, dry_run: bool = True):
        raise ValueError("blocked")

    monkeypatch.setattr("system.core.approved_autonomous_execution.LocalExecutionAdapter.run", fake_run)

    result = ApprovedAutonomousExecution(tmp_path).run()

    assert result.execution_triggered is True
    assert result.execution_result_status == "blocked"
    assert result.stopped_reason == "blocked"

