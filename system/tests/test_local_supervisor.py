from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.local_supervisor import LocalSupervisor


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
    supervisor._load_open_issues = lambda: []
    result = supervisor.run(execution_flag=False)
    assert result.execution_mode == "dry_run"
    assert result.supervisor_state == "ready"
    assert result.next_eligible_work_item.startswith("Issue #28:")
    assert result.selection_reason == "acceptance_issue_open"
    assert result.selected_issue_number == 28
    assert result.selected_issue_title == "ACCEPTANCE-0001: Single Product Vertical Slice"
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
    supervisor._load_open_issues = lambda: []
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "idle"
    assert result.next_eligible_work_item is None
    assert result.selection_reason == "idle_no_eligible_candidate"
    assert result.selected_issue_number is None
    assert result.selected_issue_title is None


def test_local_supervisor_selects_work_planner_candidate(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[{"title":"EP-0200 Work Planner Validation","status":"ready"}]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    supervisor._load_open_issues = lambda: []
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "ready"
    assert result.next_eligible_work_item == "EP-0200 Work Planner Validation"
    assert result.selection_reason == "work_planner_candidate"
    assert result.selected_issue_number is None
    assert result.selected_issue_title == "EP-0200 Work Planner Validation"


def test_local_supervisor_idles_without_candidates(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    supervisor._load_open_issues = lambda: []
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "idle"
    assert result.next_eligible_work_item is None
    assert result.selection_reason == "idle_no_eligible_candidate"


def test_local_supervisor_selects_open_product_issue(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[{"title":"EP-0200 Work Planner Validation","status":"ready"}]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    supervisor._load_open_issues = lambda: [
        {"number": 31, "title": "CONTENT-0001 Draft Review", "state": "open"},
        {"number": 30, "title": "PRODUCT-0001 Launch Checklist", "state": "open"},
        {"number": 32, "title": "PRODUCT-0002 Second Product", "state": "open"},
    ]
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "ready"
    assert result.selected_issue_number == 30
    assert result.selected_issue_title == "PRODUCT-0001 Launch Checklist"
    assert result.selection_reason == "issue_intake"
    assert result.next_eligible_work_item == "Issue #30: PRODUCT-0001 Launch Checklist"


def test_local_supervisor_accepts_uppercase_open_state(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    supervisor._load_open_issues = lambda: [{"number": 30, "title": "PRODUCT-0001 Launch Checklist", "state": "OPEN"}]
    result = supervisor.run(execution_flag=False)
    assert result.selected_issue_number == 30
    assert result.supervisor_state == "ready"


def test_local_supervisor_rejects_closed_states(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    supervisor._load_open_issues = lambda: [{"number": 30, "title": "PRODUCT-0001 Launch Checklist", "state": "CLOSED"}]
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "idle"
    assert result.selected_issue_number is None


def test_local_supervisor_selects_open_content_issue_when_no_product(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[{"title":"EP-0200 Work Planner Validation","status":"ready"}]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    supervisor._load_open_issues = lambda: [
        {"number": 31, "title": "CONTENT-0001 Draft Review", "state": "open"},
        {"number": 28, "title": "ACCEPTANCE-0001: Single Product Vertical Slice", "state": "completed"},
    ]
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "ready"
    assert result.selected_issue_number == 31
    assert result.selected_issue_title == "CONTENT-0001 Draft Review"
    assert result.selection_reason == "issue_intake"


def test_local_supervisor_idles_when_no_eligible_issues_exist(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[]}), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    supervisor._load_open_issues = lambda: [
        {"number": 28, "title": "ACCEPTANCE-0001: Single Product Vertical Slice", "state": "completed"},
        {"number": 40, "title": "FIX-0001 Repair", "state": "open"},
    ]
    result = supervisor.run(execution_flag=False)
    assert result.supervisor_state == "idle"
    assert result.next_eligible_work_item is None
    assert result.selection_reason == "idle_no_eligible_candidate"


def test_local_supervisor_skips_completed_issue_marker_and_selects_next_issue(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    (tmp_path / "runtime" / "work_planner").mkdir(parents=True)
    (tmp_path / "runtime" / "work_planner" / "latest.json").write_text(json.dumps({"candidate_items":[]}), encoding="utf-8")
    (tmp_path / "runtime" / "github").mkdir(parents=True)
    (tmp_path / "runtime" / "github" / "open_issues.json").write_text(json.dumps([
        {"number": 30, "title": "PRODUCT-0001: Product Launch Checklist", "state": "open"},
        {"number": 31, "title": "CONTENT-0001: Content Draft Review", "state": "open"},
        {"number": 32, "title": "PRODUCT-0002: Product Launch Follow-up", "state": "open"},
    ]), encoding="utf-8")
    (tmp_path / "runtime" / "issues" / "completed").mkdir(parents=True)
    (tmp_path / "runtime" / "issues" / "completed" / "issue_0030.json").write_text(json.dumps({
        "issue_number": 30,
        "issue_title": "PRODUCT-0001: Product Launch Checklist",
        "commit_sha": "2006a35",
        "completed_at": "deterministic",
        "deliverables": []
    }), encoding="utf-8")
    (tmp_path / "runtime" / "product_acceptance").mkdir(parents=True)
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    assert result.selected_issue_number == 32
    assert result.selected_issue_title == "PRODUCT-0002: Product Launch Follow-up"
    updated_open_issues = json.loads((tmp_path / "runtime" / "github" / "open_issues.json").read_text(encoding="utf-8"))
    assert all(issue["number"] != 30 for issue in updated_open_issues)
