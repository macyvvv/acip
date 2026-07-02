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

