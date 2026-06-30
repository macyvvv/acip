from __future__ import annotations

import json
from pathlib import Path

from system.core.kpi_store import update_kpi
from system.orchestrator.local_supervisor import LocalSupervisor


def _prepare_state(tmp_path: Path) -> None:
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
        json.dumps([{"number": 32, "title": "PRODUCT-0002: Product Launch Follow-up", "state": "open"}]),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "config").mkdir(parents=True)
    (tmp_path / "runtime" / "config" / "optimization.json").write_text(
        json.dumps({"enabled": False, "allowed_types": ["model_selection"]}),
        encoding="utf-8",
    )


def _enable_optimization(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "config" / "optimization.json").write_text(
        json.dumps({"enabled": True, "allowed_types": ["model_selection"]}),
        encoding="utf-8",
    )


def test_optimization_disabled_no_change(tmp_path: Path) -> None:
    _prepare_state(tmp_path)
    update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    update_kpi(True, tmp_path, issue_number=33)
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)

    request = json.loads((tmp_path / "runtime" / "request" / "execution_request.json").read_text(encoding="utf-8"))
    assert result.optimization_applied is False
    assert request["preferred_model"] == "gpt-5.4-mini"
    assert "model_override" not in request


def test_optimization_enabled_changes_model(tmp_path: Path) -> None:
    _prepare_state(tmp_path)
    _enable_optimization(tmp_path)
    for _ in range(3):
        update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)

    request = json.loads((tmp_path / "runtime" / "request" / "execution_request.json").read_text(encoding="utf-8"))
    assert result.optimization_applied is True
    assert result.optimization_type == "model_selection"
    assert request["model_override"] == "gpt-5.3-mini"
    assert request["preferred_model"] == "gpt-5.4-mini"


def test_revert_after_failed_optimization(tmp_path: Path) -> None:
    _prepare_state(tmp_path)
    _enable_optimization(tmp_path)
    for _ in range(3):
        update_kpi(False, tmp_path, issue_number=32, error_type="external_capacity")
    supervisor = LocalSupervisor(tmp_path)
    supervisor.run(execution_flag=False)
    (tmp_path / "runtime" / "local_execution").mkdir(parents=True)
    (tmp_path / "runtime" / "local_execution" / "latest.json").write_text(
        json.dumps(
            {
                "resolved_model": "gpt-5.3-mini",
                "failure_reason": "missing_deliverables",
            }
        ),
        encoding="utf-8",
    )

    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    request = json.loads((tmp_path / "runtime" / "request" / "execution_request.json").read_text(encoding="utf-8"))

    assert result.optimization_applied is False
    assert request["preferred_model"] == "gpt-5.4-mini"
    assert "model_override" not in request
