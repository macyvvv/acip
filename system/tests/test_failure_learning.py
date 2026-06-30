from __future__ import annotations

import json
from pathlib import Path

from system.core.failure_learning import analyze_failure_history, load_failure_rules, write_failure_rules
from system.core.failure_store import append_failure
from system.orchestrator.local_supervisor import LocalSupervisor


def test_repeated_failures_generate_rule(tmp_path: Path) -> None:
    for i in range(3):
        append_failure(
            {
                "request_id": f"REQ-{i}",
                "issue_number": 32,
                "error_type": "external_capacity",
                "model": "gpt-5.4-mini",
            },
            base_path=tmp_path,
        )
    rules = analyze_failure_history(tmp_path)
    assert len(rules) == 1
    assert rules[0]["issue_number"] == 32
    assert rules[0]["error_type"] == "external_capacity"
    assert rules[0]["action"] == "temporary_skip"
    assert rules[0]["threshold"] == 3
    assert rules[0]["cooldown_seconds"] == 300
    assert rules[0]["last_failed_at"]


def test_failure_rules_are_persisted(tmp_path: Path) -> None:
    for i in range(3):
        append_failure(
            {
                "request_id": f"REQ-{i}",
                "issue_number": 32,
                "error_type": "external_capacity",
                "model": "gpt-5.4-mini",
            },
            base_path=tmp_path,
        )
    rules = write_failure_rules(tmp_path)
    path = tmp_path / "system" / "runtime" / "knowledge" / "failure_rules.json"
    assert path.exists()
    assert load_failure_rules(tmp_path) == rules
    assert json.loads(path.read_text(encoding="utf-8")) == rules


def test_supervisor_respects_failure_rules(tmp_path: Path) -> None:
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
    (tmp_path / "runtime" / "github").mkdir(parents=True)
    (tmp_path / "runtime" / "github" / "open_issues.json").write_text(
        json.dumps([
            {"number": 32, "title": "PRODUCT-0002: Product Launch Follow-up", "state": "open"},
            {"number": 31, "title": "CONTENT-0001: Content Draft Review", "state": "open"},
        ]),
        encoding="utf-8",
    )
    (tmp_path / "system" / "runtime" / "knowledge").mkdir(parents=True)
    (tmp_path / "system" / "runtime" / "knowledge" / "failure_rules.json").write_text(
        json.dumps([
            {"issue_number": 32, "error_type": "external_capacity", "action": "temporary_skip", "threshold": 3, "cooldown_seconds": 300}
        ]),
        encoding="utf-8",
    )
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    assert result.selected_issue_number == 31
    assert result.selection_reason == "skipped_due_to_failure_history"
