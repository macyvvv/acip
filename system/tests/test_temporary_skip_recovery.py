from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from system.core.failure_store import append_failure
from system.core.failure_learning import write_failure_rules
from system.orchestrator.local_supervisor import LocalSupervisor


def _prepare_supervisor_state(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(
        json.dumps(
            {
                "mission": "Build",
                "current_objective": "Publish",
                "current_pack": "PACK-0011",
                "current_ep": "EP-0187",
                "approved_next_action": "draft",
                "parking_lot": [],
                "refactoring_priorities": [],
                "blocked_items": [],
                "approval_required": False,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(
        json.dumps({"repository_health": "healthy", "approval_required": False, "next_action": "draft"}),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items": []}), encoding="utf-8")
    (tmp_path / "runtime" / "github").mkdir(parents=True)
    (tmp_path / "runtime" / "github" / "open_issues.json").write_text(
        json.dumps(
            [
                {"number": 32, "title": "PRODUCT-0002: Product Launch Follow-up", "state": "open"},
                {"number": 33, "title": "PRODUCT-0003: Product Launch Follow-up", "state": "open"},
            ]
        ),
        encoding="utf-8",
    )


def test_skip_within_cooldown(tmp_path: Path) -> None:
    _prepare_supervisor_state(tmp_path)
    write_failure_rules(
        tmp_path,
        [{"issue_number": 32, "error_type": "external_capacity", "action": "temporary_skip", "threshold": 3, "cooldown_seconds": 300, "last_failed_at": datetime.now(timezone.utc).isoformat()}],
    )
    append_failure(
        {
            "request_id": "REQ-1",
            "issue_number": 32,
            "error_type": "external_capacity",
            "model": "gpt-5.4-mini",
            "last_failed_at": datetime.now(timezone.utc).isoformat(),
        },
        base_path=tmp_path,
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)

    assert result.selected_issue_number == 33
    assert result.selection_reason == "skipped_due_to_failure_history"


def test_retry_after_cooldown(tmp_path: Path) -> None:
    _prepare_supervisor_state(tmp_path)
    old_time = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
    write_failure_rules(
        tmp_path,
        [{"issue_number": 32, "error_type": "external_capacity", "action": "temporary_skip", "threshold": 3, "cooldown_seconds": 300, "last_failed_at": old_time}],
    )
    append_failure(
        {
            "request_id": "REQ-1",
            "issue_number": 32,
            "error_type": "external_capacity",
            "model": "gpt-5.4-mini",
            "last_failed_at": old_time,
        },
        base_path=tmp_path,
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)

    assert result.selected_issue_number == 32
    assert result.selection_reason == "cooldown_expired_retry"


def test_skipped_issue_reintroduced_into_candidates(tmp_path: Path) -> None:
    _prepare_supervisor_state(tmp_path)
    old_time = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
    write_failure_rules(
        tmp_path,
        [{"issue_number": 32, "error_type": "external_capacity", "action": "temporary_skip", "threshold": 3, "cooldown_seconds": 300, "last_failed_at": old_time}],
    )
    append_failure(
        {
            "request_id": "REQ-1",
            "issue_number": 32,
            "error_type": "external_capacity",
            "model": "gpt-5.4-mini",
            "last_failed_at": old_time,
        },
        base_path=tmp_path,
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)

    assert result.selected_issue_number == 32
    assert result.selection_reason == "cooldown_expired_retry"


def test_repeated_failures_update_cooldown(tmp_path: Path) -> None:
    _prepare_supervisor_state(tmp_path)
    old_time = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
    append_failure(
        {
            "request_id": "REQ-1",
            "issue_number": 32,
            "error_type": "external_capacity",
            "model": "gpt-5.4-mini",
            "last_failed_at": old_time,
        },
        base_path=tmp_path,
    )
    append_failure(
        {
            "request_id": "REQ-2",
            "issue_number": 32,
            "error_type": "external_capacity",
            "model": "gpt-5.4-mini",
            "last_failed_at": old_time,
        },
        base_path=tmp_path,
    )
    latest_failure = append_failure(
        {
            "request_id": "REQ-3",
            "issue_number": 32,
            "error_type": "external_capacity",
            "model": "gpt-5.4-mini",
            "last_failed_at": old_time,
        },
        base_path=tmp_path,
    )
    assert latest_failure["retry_count"] == 3
    assert latest_failure["last_failed_at"]
