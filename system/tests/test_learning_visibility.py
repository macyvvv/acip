from __future__ import annotations

import json
from pathlib import Path

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
                {"number": 31, "title": "CONTENT-0001: Content Draft Review", "state": "open"},
            ]
        ),
        encoding="utf-8",
    )


def test_rule_applied_fields_populated(tmp_path: Path) -> None:
    _prepare_supervisor_state(tmp_path)
    write_failure_rules(
        tmp_path,
        [{"issue_number": 32, "error_type": "external_capacity", "action": "skip", "threshold": 3}],
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)

    assert result.selected_issue_number == 31
    assert result.applied_learning_rule == {
        "issue_number": 32,
        "error_type": "external_capacity",
        "threshold": 3,
    }
    assert result.learning_reason == "issue 32 skipped due to repeated external_capacity failures (threshold 3)"


def test_no_rule_means_null_fields(tmp_path: Path) -> None:
    _prepare_supervisor_state(tmp_path)
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)

    assert result.applied_learning_rule is None
    assert result.learning_reason == ""


def test_learning_summary_is_written(tmp_path: Path) -> None:
    _prepare_supervisor_state(tmp_path)
    write_failure_rules(
        tmp_path,
        [
            {"issue_number": 32, "error_type": "external_capacity", "action": "skip", "threshold": 3},
            {"issue_number": 31, "error_type": "usage_limit", "action": "skip", "threshold": 3},
        ],
    )
    summary_path = tmp_path / "system" / "runtime" / "knowledge" / "learning_summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["total_failures"] == 0
    assert summary["total_rules"] == 2
    assert summary["issues_with_rules"] == [31, 32]
    assert isinstance(summary["last_updated"], str)
