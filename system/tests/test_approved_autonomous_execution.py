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

    # market_research's next_roles == ("marketing",) -- success should have
    # auto-enqueued and activated it at its own per-task scope (Level 2: no
    # shared slot, so this never touches the legacy top-level handoff file).
    queue = json.loads((tmp_path / "system" / "runtime" / "business_agent_tasks" / "queue.json").read_text(encoding="utf-8"))
    assert len(queue) == 1
    assert queue[0]["role_id"] == "marketing"
    assert queue[0]["source"] == "auto_trigger"
    new_handoff_path = tmp_path / "system" / "runtime" / "agent_handoff" / "scopes" / "text_syndicate" / "marketing" / queue[0]["task_id"] / "handoff.json"
    assert new_handoff_path.exists()
    new_handoff = json.loads(new_handoff_path.read_text(encoding="utf-8"))
    assert new_handoff["role_id"] == "marketing"
    # per-scope execution result, not the shared top-level file
    scope_result_path = tmp_path / "system" / "runtime" / "agent_execution" / "scopes" / "text_syndicate" / "market_research" / "task-0001" / "latest.json"
    assert scope_result_path.exists()


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
    # never chain off a failure
    assert not (tmp_path / "system" / "runtime" / "business_agent_tasks" / "queue.json").exists()


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


def test_scope_parameterized_run_uses_per_task_approval(tmp_path: Path, monkeypatch) -> None:
    from system.core.business_agent_handoff import scope_dir, write_business_agent_handoff

    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc", tmp_path)
    approval_path = scope_dir("text_syndicate", "market_research", "task-0001", tmp_path) / "approval.json"
    _write_approval(approval_path, handoff_id="REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001", scope_type="business_role_task", scope_id="text_syndicate:market_research:task-0001")

    class FakeOutcome:
        success = True
        artifact_path = "system/runtime/business_agents/text_syndicate/market_research/task-0001/latest.json"
        exit_code = 0

    def fake_run(self, **kwargs):
        return FakeOutcome()

    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", fake_run)

    result = ApprovedAutonomousExecution(tmp_path).run(business_id="text_syndicate", role_id="market_research", task_id="task-0001")

    assert result.execution_triggered is True
    assert result.execution_result_status == "success"
    # per-scope result, not the shared top-level agent_execution/latest.json
    assert (tmp_path / "system" / "runtime" / "agent_execution" / "scopes" / "text_syndicate" / "market_research" / "task-0001" / "latest.json").exists()


def test_two_businesses_execute_independently_without_interference(tmp_path: Path, monkeypatch) -> None:
    # Concurrency/no-interference test: business A's approved-and-pending
    # scope executes correctly, and business B's separately approved scope
    # also executes correctly, with neither's result or approval state
    # touched by the other.
    from system.core.business_agent_handoff import scope_dir, write_business_agent_handoff

    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc A", tmp_path)
    _write_approval(
        scope_dir("text_syndicate", "market_research", "task-0001", tmp_path) / "approval.json",
        handoff_id="REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001",
        scope_type="business_role_task",
        scope_id="text_syndicate:market_research:task-0001",
    )
    write_business_agent_handoff("kabukicho_survival_map", "marketing", "task-0007", "desc B", tmp_path)
    _write_approval(
        scope_dir("kabukicho_survival_map", "marketing", "task-0007", tmp_path) / "approval.json",
        handoff_id="REQ-KABUKICHO-SURVIVAL-MAP-MARKETING-TASK-0007",
        scope_type="business_role_task",
        scope_id="kabukicho_survival_map:marketing:task-0007",
    )

    calls: list[dict] = []

    class FakeOutcome:
        success = True
        exit_code = 0

        def __init__(self, artifact_path):
            self.artifact_path = artifact_path

    def fake_run(self, *, business_id, role_id, task_id, task_description="", approval_flag=False, dry_run=True):
        calls.append({"business_id": business_id, "role_id": role_id, "task_id": task_id})
        return FakeOutcome(f"system/runtime/business_agents/{business_id}/{role_id}/{task_id}/latest.json")

    monkeypatch.setattr("system.core.approved_autonomous_execution.BusinessAgentExecutionAdapter.run", fake_run)

    result_a = ApprovedAutonomousExecution(tmp_path).run(business_id="text_syndicate", role_id="market_research", task_id="task-0001")
    result_b = ApprovedAutonomousExecution(tmp_path).run(business_id="kabukicho_survival_map", role_id="marketing", task_id="task-0007")

    assert result_a.execution_result_status == "success"
    assert result_b.execution_result_status == "success"
    assert {c["business_id"] for c in calls} == {"text_syndicate", "kabukicho_survival_map"}

    a_result_path = tmp_path / "system" / "runtime" / "agent_execution" / "scopes" / "text_syndicate" / "market_research" / "task-0001" / "latest.json"
    b_result_path = tmp_path / "system" / "runtime" / "agent_execution" / "scopes" / "kabukicho_survival_map" / "marketing" / "task-0007" / "latest.json"
    assert a_result_path.exists()
    assert b_result_path.exists()
    import json as _json
    assert _json.loads(a_result_path.read_text())["scope_id"] == "text_syndicate:market_research:task-0001"
    assert _json.loads(b_result_path.read_text())["scope_id"] == "kabukicho_survival_map:marketing:task-0007"

