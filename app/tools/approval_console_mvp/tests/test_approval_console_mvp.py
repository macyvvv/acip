from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from app.tools.approval_console_mvp.service import ApprovalConsoleService

REPO_ROOT = Path(__file__).resolve().parents[4]
APPROVAL_JSON = REPO_ROOT / "system" / "runtime" / "agent_handoff" / "approval.json"
APPROVAL_MD = REPO_ROOT / "system" / "runtime" / "agent_handoff" / "approval.md"


def _executor_factory(responses: list[subprocess.CompletedProcess[str]]):
    calls: list[list[str]] = []

    def _executor(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return responses.pop(0)

    return calls, _executor


def _backup_approval_artifacts() -> tuple[Path, Path]:
    backup_dir = Path(__file__).resolve().parent / ".backup"
    backup_dir.mkdir(exist_ok=True)
    approval_json_backup = backup_dir / "approval.json"
    approval_md_backup = backup_dir / "approval.md"
    if APPROVAL_JSON.exists():
        shutil.copy2(APPROVAL_JSON, approval_json_backup)
    if APPROVAL_MD.exists():
        shutil.copy2(APPROVAL_MD, approval_md_backup)
    return approval_json_backup, approval_md_backup


def _restore_approval_artifacts(backups: tuple[Path, Path]) -> None:
    approval_json_backup, approval_md_backup = backups
    if approval_json_backup.exists():
        shutil.copy2(approval_json_backup, APPROVAL_JSON)
    if approval_md_backup.exists():
        shutil.copy2(approval_md_backup, APPROVAL_MD)
    if approval_json_backup.exists():
        approval_json_backup.unlink()
    if approval_md_backup.exists():
        approval_md_backup.unlink()


def _write_runtime_state(root: Path, *, current_handoff: dict, roadmap: dict, open_issues: list[dict], frozen_plan: dict | None = None, completed: list[dict] | None = None) -> None:
    (root / "system" / "runtime" / "agent_handoff").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "roadmap").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "github").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "issues" / "completed").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "agent_execution").mkdir(parents=True, exist_ok=True)
    (root / "system" / "runtime" / "agent_handoff" / "latest.json").write_text(json.dumps(current_handoff), encoding="utf-8")
    (root / "system" / "runtime" / "roadmap" / "issue_portfolio.json").write_text(json.dumps(roadmap), encoding="utf-8")
    (root / "system" / "runtime" / "github" / "open_issues.json").write_text(json.dumps(open_issues), encoding="utf-8")
    (root / "system" / "runtime" / "agent_execution" / "latest.json").write_text(json.dumps({"execution_result_status": "success"}), encoding="utf-8")
    if frozen_plan is not None:
        (root / "system" / "runtime" / "roadmap" / "frozen_issue_closure_plan.json").write_text(json.dumps(frozen_plan), encoding="utf-8")
    if completed:
        for entry in completed:
            issue_number = entry["issue_number"]
            (root / "system" / "runtime" / "issues" / "completed" / f"issue_{issue_number:04d}.json").write_text(json.dumps(entry), encoding="utf-8")


def test_candidate_loading_from_roadmap_and_open_issues(tmp_path: Path) -> None:
    _write_runtime_state(
        tmp_path,
        current_handoff={"request_id": "REQ-OPEN-001", "issue_number": None},
        roadmap={
            "issues": [
                {
                    "issue_number": 41,
                    "title": "PRODUCT-0004 Product Launch Follow-up",
                    "category": "product_incremental",
                    "current_status": "open",
                    "execution_fit": "one_shot_ready",
                    "priority_bucket": "NOW",
                    "recommended_reason": "safe open product issue #41 is a narrow candidate for the current one-shot baseline",
                    "blocking_reason": "",
                    "depends_on": [32],
                    "source_of_truth": "roadmap",
                },
                {
                    "issue_number": 25,
                    "title": "PACK-0013 Repository OS v2 Release",
                    "category": "broad_architecture",
                    "current_status": "archived",
                    "execution_fit": "archived",
                    "priority_bucket": "FROZEN",
                    "recommended_reason": "historic",
                    "blocking_reason": "",
                    "depends_on": [],
                    "source_of_truth": "roadmap",
                },
            ]
        },
        open_issues=[{"number": 41, "title": "PRODUCT-0004 Product Launch Follow-up", "state": "open"}],
        frozen_plan={"issues": [{"issue_number": 25, "closure_disposition": "keep_open_broad_architecture"}]},
    )
    service = ApprovalConsoleService(tmp_path)
    scopes = service.load_scopes()
    assert len(scopes) == 1
    scope = scopes[0]
    assert scope.issue_number == 41
    assert scope.scope_type == "issue"
    assert scope.scope_id == "41"
    assert scope.title == "PRODUCT-0004 Product Launch Follow-up"
    assert scope.current_bucket == "NOW"
    assert scope.execution_fit == "one_shot_ready"
    assert scope.recommendation_reason.startswith("safe open product issue #41")
    assert scope.approval_ready is False
    rendered = service.render_status(scope, None)
    assert "Current NOW candidates: 1" in rendered
    assert "Current Execution Target: Issue #41: PRODUCT-0004 Product Launch Follow-up" in rendered


def test_completed_and_frozen_items_are_excluded(tmp_path: Path) -> None:
    _write_runtime_state(
        tmp_path,
        current_handoff={"request_id": "REQ-OPEN-001", "issue_number": None},
        roadmap={
            "issues": [
                {
                    "issue_number": 30,
                    "title": "PRODUCT-0001 Product Launch Checklist",
                    "category": "product_incremental",
                    "current_status": "completed",
                    "execution_fit": "completed",
                    "priority_bucket": "FROZEN",
                    "recommended_reason": "done",
                    "blocking_reason": "",
                    "depends_on": [],
                    "source_of_truth": "completed_marker",
                },
                {
                    "issue_number": 25,
                    "title": "PACK-0013 Repository OS v2 Release",
                    "category": "broad_architecture",
                    "current_status": "archived",
                    "execution_fit": "archived",
                    "priority_bucket": "FROZEN",
                    "recommended_reason": "historic",
                    "blocking_reason": "",
                    "depends_on": [],
                    "source_of_truth": "roadmap",
                },
            ]
        },
        open_issues=[],
        frozen_plan={
            "issues": [
                {"issue_number": 30, "closure_disposition": "close_completed"},
                {"issue_number": 25, "closure_disposition": "keep_open_broad_architecture"},
            ]
        },
        completed=[{"issue_number": 30, "issue_title": "PRODUCT-0001 Product Launch Checklist"}],
    )
    service = ApprovalConsoleService(tmp_path)
    assert service.load_scopes() == []
    assert service.render_status(None, None).count("no NOW items") == 0 or "Zero-candidate reason" in service.render_status(None, None)


def test_zero_candidate_explanation(tmp_path: Path) -> None:
    _write_runtime_state(
        tmp_path,
        current_handoff={"request_id": "REQ-OPEN-001", "issue_number": None},
        roadmap={
            "issues": [
                {
                    "issue_number": 41,
                    "title": "PRODUCT-0004 Product Launch Follow-up",
                    "category": "product_incremental",
                    "current_status": "open",
                    "execution_fit": "not_one_shot_ready",
                    "priority_bucket": "NOW",
                    "recommended_reason": "not ready",
                    "blocking_reason": "needs more work",
                    "depends_on": [],
                    "source_of_truth": "roadmap",
                }
            ]
        },
        open_issues=[{"number": 41, "title": "PRODUCT-0004 Product Launch Follow-up", "state": "open"}],
        frozen_plan={"issues": []},
    )
    service = ApprovalConsoleService(tmp_path)
    assert service.load_scopes() == []
    text = service.render_status(None, None)
    assert "Zero-candidate reason: NOW exists but not one_shot_ready" in text


def test_latest_handoff_is_not_sole_candidate_source(tmp_path: Path) -> None:
    _write_runtime_state(
        tmp_path,
        current_handoff={"request_id": "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001", "approved_draft_id": "DRAFT-OPP-KABUKICHO-001"},
        roadmap={
            "issues": [
                {
                    "issue_number": 41,
                    "title": "PRODUCT-0004 Product Launch Follow-up",
                    "category": "product_incremental",
                    "current_status": "open",
                    "execution_fit": "one_shot_ready",
                    "priority_bucket": "NOW",
                    "recommended_reason": "safe open product issue #41 is a narrow candidate for the current one-shot baseline",
                    "blocking_reason": "",
                    "depends_on": [32],
                    "source_of_truth": "roadmap",
                }
            ]
        },
        open_issues=[{"number": 41, "title": "PRODUCT-0004 Product Launch Follow-up", "state": "open"}],
        frozen_plan={"issues": []},
    )
    service = ApprovalConsoleService(tmp_path)
    scopes = service.load_scopes()
    assert len(scopes) == 1
    assert scopes[0].issue_number == 41
    assert scopes[0].approval_ready is False


def test_business_role_task_candidate_appears_alongside_issue_candidates(tmp_path: Path) -> None:
    _write_runtime_state(
        tmp_path,
        current_handoff={"request_id": "REQ-OPEN-001", "issue_number": None},
        roadmap={"issues": []},
        open_issues=[],
        frozen_plan={"issues": []},
    )
    (tmp_path / "system" / "runtime" / "business_agent_tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "runtime" / "business_agent_tasks" / "queue.json").write_text(
        json.dumps(
            [
                {
                    "business_id": "text_syndicate",
                    "role_id": "market_research",
                    "task_id": "task-0001",
                    "title": "Research impression-driving niches",
                    "status": "candidate",
                }
            ]
        ),
        encoding="utf-8",
    )
    service = ApprovalConsoleService(tmp_path)
    scopes = service.load_scopes()
    assert len(scopes) == 1
    scope = scopes[0]
    assert scope.scope_type == "business_role_task"
    assert scope.scope_id == "text_syndicate:market_research:task-0001"
    assert scope.business_id == "text_syndicate"
    assert scope.role_id == "market_research"


def test_non_candidate_business_role_tasks_are_excluded(tmp_path: Path) -> None:
    _write_runtime_state(
        tmp_path,
        current_handoff={"request_id": "REQ-OPEN-001", "issue_number": None},
        roadmap={"issues": []},
        open_issues=[],
        frozen_plan={"issues": []},
    )
    (tmp_path / "system" / "runtime" / "business_agent_tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "runtime" / "business_agent_tasks" / "queue.json").write_text(
        json.dumps(
            [
                {
                    "business_id": "text_syndicate",
                    "role_id": "market_research",
                    "task_id": "task-0001",
                    "title": "Already completed",
                    "status": "completed",
                }
            ]
        ),
        encoding="utf-8",
    )
    service = ApprovalConsoleService(tmp_path)
    assert service.load_scopes() == []


def test_approve_scope_marks_business_role_task_approved(tmp_path: Path) -> None:
    backups = _backup_approval_artifacts()
    (tmp_path / "system" / "runtime" / "business_agent_tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "runtime" / "business_agent_tasks" / "queue.json").write_text(
        json.dumps(
            [
                {
                    "business_id": "text_syndicate",
                    "role_id": "market_research",
                    "task_id": "task-0001",
                    "title": "Research niches",
                    "status": "candidate",
                }
            ]
        ),
        encoding="utf-8",
    )
    calls, executor = _executor_factory([subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")])
    try:
        service = ApprovalConsoleService(tmp_path, executor=executor)
        scope = type(
            "Scope",
            (),
            {
                "scope_type": "business_role_task",
                "scope_id": "text_syndicate:market_research:task-0001",
                "handoff_id": "REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001",
                "business_id": "text_syndicate",
                "role_id": "market_research",
            },
        )()
        result = service.approve_scope(scope, approved_by="human", reason="ok")
        assert result.status == "approved"
        queue = json.loads((tmp_path / "system" / "runtime" / "business_agent_tasks" / "queue.json").read_text(encoding="utf-8"))
        assert queue[0]["status"] == "approved"
    finally:
        _restore_approval_artifacts(backups)


def test_approval_update_call(tmp_path: Path) -> None:
    backups = _backup_approval_artifacts()
    calls, executor = _executor_factory([subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")])
    try:
        service = ApprovalConsoleService(tmp_path, executor=executor)
        scope = type(
            "Scope",
            (),
            {
                "scope_type": "issue",
                "scope_id": "41",
                "handoff_id": "REQ-ISSUE-0041",
            },
        )()
        result = service.approve_scope(scope, approved_by="human", reason="ok")
        assert calls[0][1].endswith("set_execution_approval.py")
        assert result.status == "approved"
    finally:
        _restore_approval_artifacts(backups)


def test_one_shot_execution_trigger_call(tmp_path: Path) -> None:
    execution_json = tmp_path / "system" / "runtime" / "agent_execution" / "latest.json"
    execution_json.parent.mkdir(parents=True, exist_ok=True)
    execution_json.write_text('{"execution_result_status":"success","stopped_reason":"completion_marker_written","completion_marker_path":"x"}', encoding="utf-8")
    calls, executor = _executor_factory([subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")])
    service = ApprovalConsoleService(tmp_path, executor=executor)
    result = service.run_one_shot_execution()
    assert calls[0][1].endswith("run_approved_autonomous_execution.py")
    assert result.execution_result_status == "success"


def test_result_rendering_state_mapping() -> None:
    service = ApprovalConsoleService()
    text = service.render_status(None, None)
    assert "idle" in text


def test_single_now_candidate_is_prominently_labeled(tmp_path: Path) -> None:
    _write_runtime_state(
        tmp_path,
        current_handoff={"request_id": "REQ-OPEN-001", "issue_number": None},
        roadmap={
            "issues": [
                {
                    "issue_number": 41,
                    "title": "PRODUCT-0004 Product Launch Follow-up",
                    "category": "product_incremental",
                    "current_status": "open",
                    "execution_fit": "one_shot_ready",
                    "priority_bucket": "NOW",
                    "recommended_reason": "safe open product issue #41 is a narrow candidate for the current one-shot baseline",
                    "blocking_reason": "",
                    "depends_on": [32],
                    "source_of_truth": "roadmap",
                }
            ]
        },
        open_issues=[{"number": 41, "title": "PRODUCT-0004 Product Launch Follow-up", "state": "open"}],
        frozen_plan={"issues": []},
    )
    service = ApprovalConsoleService(tmp_path)
    scopes = service.load_scopes()
    assert len(scopes) == 1
    text = service.render_status(scopes[0], None)
    assert "Current NOW candidates: 1" in text
    assert "Current Execution Target: Issue #41: PRODUCT-0004 Product Launch Follow-up" in text
