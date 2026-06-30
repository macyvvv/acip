from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.local_supervisor import LocalSupervisor
from system.core.failure_learning import write_failure_rules


def _write_base_state(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(
        json.dumps({
            "mission": "Build",
            "current_objective": "Publish",
            "current_pack": "PACK-0011",
            "current_ep": "EP-0187",
            "approved_next_action": "draft",
            "parking_lot": [],
            "refactoring_priorities": [],
            "blocked_items": [],
            "approval_required": False,
        }),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(
        json.dumps({"repository_health": "healthy", "approval_required": False, "next_action": "draft"}),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items": []}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)


def test_failure_history_below_threshold_keeps_normal_selection(tmp_path: Path) -> None:
    _write_base_state(tmp_path)
    (tmp_path / "runtime" / "github").mkdir(parents=True)
    (tmp_path / "runtime" / "github" / "open_issues.json").write_text(
        json.dumps([
            {"number": 32, "title": "PRODUCT-0002: Product Launch Follow-up", "state": "open"},
            {"number": 31, "title": "CONTENT-0001: Content Draft Review", "state": "open"},
        ]),
        encoding="utf-8",
    )
    (tmp_path / "system" / "runtime" / "knowledge").mkdir(parents=True)
    (tmp_path / "system" / "runtime" / "knowledge" / "failures.json").write_text(
        json.dumps([
            {"request_id": "REQ-1", "issue_number": 32, "error_type": "external_capacity", "model": "gpt-5.4-mini", "timestamp": "2026-01-01T00:00:00Z", "retry_count": 2},
        ]),
        encoding="utf-8",
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    assert result.selected_issue_number == 32
    assert result.selection_reason == "issue_intake"


def test_failure_history_at_threshold_skips_issue_and_falls_back(tmp_path: Path) -> None:
    _write_base_state(tmp_path)
    (tmp_path / "runtime" / "github").mkdir(parents=True)
    (tmp_path / "runtime" / "github" / "open_issues.json").write_text(
        json.dumps([
            {"number": 32, "title": "PRODUCT-0002: Product Launch Follow-up", "state": "open"},
            {"number": 31, "title": "CONTENT-0001: Content Draft Review", "state": "open"},
        ]),
        encoding="utf-8",
    )
    (tmp_path / "system" / "runtime" / "knowledge").mkdir(parents=True)
    (tmp_path / "system" / "runtime" / "knowledge" / "failures.json").write_text(
        json.dumps([
            {"request_id": "REQ-1", "issue_number": 32, "error_type": "external_capacity", "model": "gpt-5.4-mini", "timestamp": "2026-01-01T00:00:00Z", "retry_count": 3},
        ]),
        encoding="utf-8",
    )
    write_failure_rules(
        tmp_path,
        [
            {
                "issue_number": 32,
                "error_type": "external_capacity",
                "action": "temporary_skip",
                "threshold": 3,
                "cooldown_seconds": 300,
                "last_failed_at": "2026-01-01T00:00:00Z",
            }
        ],
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    assert result.selected_issue_number == 31
    assert result.selected_issue_title == "CONTENT-0001: Content Draft Review"
    assert result.selection_reason == "skipped_due_to_failure_history"


def test_failure_history_at_threshold_idles_when_no_fallback_exists(tmp_path: Path) -> None:
    _write_base_state(tmp_path)
    (tmp_path / "runtime" / "github").mkdir(parents=True)
    (tmp_path / "runtime" / "github" / "open_issues.json").write_text(
        json.dumps([
            {"number": 32, "title": "PRODUCT-0002: Product Launch Follow-up", "state": "open"},
        ]),
        encoding="utf-8",
    )
    (tmp_path / "system" / "runtime" / "knowledge").mkdir(parents=True)
    (tmp_path / "system" / "runtime" / "knowledge" / "failures.json").write_text(
        json.dumps([
            {"request_id": "REQ-1", "issue_number": 32, "error_type": "external_capacity", "model": "gpt-5.4-mini", "timestamp": "2026-01-01T00:00:00Z", "retry_count": 3},
        ]),
        encoding="utf-8",
    )
    write_failure_rules(
        tmp_path,
        [
            {
                "issue_number": 32,
                "error_type": "external_capacity",
                "action": "temporary_skip",
                "threshold": 3,
                "cooldown_seconds": 300,
                "last_failed_at": "2026-01-01T00:00:00Z",
            }
        ],
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "idle"
    assert result.next_eligible_work_item is None
    assert result.selection_reason == "idle_no_eligible_candidate"
