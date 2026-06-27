from __future__ import annotations

import json
from pathlib import Path

from orchestrator.local_supervisor import LocalSupervisor


def test_local_supervisor_writes_runtime(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[{"title":"EP-0200 Work Planner Validation"}]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    (tmp_path / "runtime" / "product_acceptance" / "acceptance_0001.json").write_text(json.dumps({"issue_number": 28, "title": "ACCEPTANCE-0001: Single Product Vertical Slice", "state": "open"}), encoding="utf-8")
    supervisor = LocalSupervisor(tmp_path)
    supervisor._fetch_issue_28 = lambda: {}
    result = supervisor.run(execution_flag=False)
    assert result.execution_mode == "dry_run"
    assert result.next_eligible_work_item.startswith("Issue #28:")
    assert (tmp_path / "runtime" / "supervisor" / "latest.json").exists()
    request = json.loads((tmp_path / "runtime" / "request" / "execution_request.json").read_text(encoding="utf-8"))
    assert request["request_id"] == "REQ-ACCEPTANCE-0001"


def test_local_supervisor_skips_completed_acceptance(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[{"title":"EP-0200 Work Planner Validation","status":"ready"}]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    (tmp_path / "runtime" / "product_acceptance" / "acceptance_0001.json").write_text(json.dumps({"issue_number": 28, "title": "ACCEPTANCE-0001: Single Product Vertical Slice", "state": "completed"}), encoding="utf-8")
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    assert "ACCEPTANCE-0001" in result.next_eligible_work_item
    assert result.next_eligible_work_item.startswith("ACCEPTANCE-0001 completed")
