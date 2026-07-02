from __future__ import annotations

import subprocess
import shutil
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


def test_candidate_loading(tmp_path: Path) -> None:
    service = ApprovalConsoleService(REPO_ROOT)
    scopes = service.load_scopes()
    assert len(scopes) == 1
    assert scopes[0].scope_type in {"approved_draft", "issue"}
    assert scopes[0].scope_id


def test_single_scope_selection() -> None:
    scope = ApprovalConsoleService(REPO_ROOT).load_scopes()[0]
    assert scope is not None


def test_approval_update_call(tmp_path: Path) -> None:
    backups = _backup_approval_artifacts()
    calls, executor = _executor_factory([subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")])
    try:
        service = ApprovalConsoleService(tmp_path, executor=executor)
        scope = type("Scope", (), {"scope_type": "approved_draft", "scope_id": "DRAFT-OPP-KABUKICHO-001", "handoff_id": "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001"})()
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
