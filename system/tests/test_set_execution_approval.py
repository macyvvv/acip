from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


from system.core.business_agent_handoff import scope_dir

SCRIPT = Path(__file__).resolve().parents[2] / "system" / "scripts" / "agent" / "set_execution_approval.py"
REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVAL_JSON = REPO_ROOT / "system" / "runtime" / "agent_handoff" / "approval.json"
APPROVAL_MD = REPO_ROOT / "system" / "runtime" / "agent_handoff" / "approval.md"


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


def _backup_approval(tmp_path: Path) -> tuple[Path, Path]:
    backup_json = tmp_path / "approval.json.bak"
    backup_md = tmp_path / "approval.md.bak"
    shutil.copy2(APPROVAL_JSON, backup_json)
    shutil.copy2(APPROVAL_MD, backup_md)
    return backup_json, backup_md


def _restore_approval(backup_json: Path, backup_md: Path) -> None:
    shutil.copy2(backup_json, APPROVAL_JSON)
    shutil.copy2(backup_md, APPROVAL_MD)


def test_approved_execution_enabled_true_works(tmp_path: Path) -> None:
    backup_json, backup_md = _backup_approval(tmp_path)
    try:
        result = _run(
            tmp_path,
            "--scope-type",
            "approved_draft",
            "--scope-id",
            "DRAFT-OPP-KABUKICHO-001",
            "--handoff-id",
            "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
            "--decision-status",
            "approved",
            "--execution-enabled",
            "true",
            "--approved-by",
            "human",
            "--reason",
            "Approved for one-shot autonomous execution under the current operational baseline.",
        )

        assert result.returncode == 0, result.stderr
        assert APPROVAL_JSON.exists()
        assert APPROVAL_MD.exists()
        payload = json.loads(APPROVAL_JSON.read_text(encoding="utf-8"))
        assert payload["decision_status"] == "approved"
        assert payload["execution_enabled"] is True
    finally:
        _restore_approval(backup_json, backup_md)


def test_pending_execution_enabled_true_rejected(tmp_path: Path) -> None:
    backup_json, backup_md = _backup_approval(tmp_path)
    try:
        result = _run(
            tmp_path,
            "--scope-type",
            "approved_draft",
            "--scope-id",
            "DRAFT-OPP-KABUKICHO-001",
            "--handoff-id",
            "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
            "--decision-status",
            "pending",
            "--execution-enabled",
            "true",
            "--approved-by",
            "human",
            "--reason",
            "Pending approval",
        )

        assert result.returncode != 0
        assert "only allowed when decision_status=approved" in result.stderr or "only allowed when decision_status=approved" in result.stdout
    finally:
        _restore_approval(backup_json, backup_md)


def test_rejected_execution_enabled_true_rejected(tmp_path: Path) -> None:
    backup_json, backup_md = _backup_approval(tmp_path)
    try:
        result = _run(
            tmp_path,
            "--scope-type",
            "approved_draft",
            "--scope-id",
            "DRAFT-OPP-KABUKICHO-001",
            "--handoff-id",
            "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
            "--decision-status",
            "rejected",
            "--execution-enabled",
            "true",
            "--approved-by",
            "human",
            "--reason",
            "Rejected approval",
        )

        assert result.returncode != 0
    finally:
        _restore_approval(backup_json, backup_md)


def test_missing_required_fields_fails(tmp_path: Path) -> None:
    backup_json, backup_md = _backup_approval(tmp_path)
    try:
        result = _run(
            tmp_path,
            "--scope-type",
            "approved_draft",
            "--scope-id",
            "DRAFT-OPP-KABUKICHO-001",
            "--handoff-id",
            "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
            "--decision-status",
            "approved",
            "--execution-enabled",
            "true",
            "--approved-by",
            "human",
        )

        assert result.returncode != 0
    finally:
        _restore_approval(backup_json, backup_md)


def test_approval_md_refreshed(tmp_path: Path) -> None:
    backup_json, backup_md = _backup_approval(tmp_path)
    try:
        result = _run(
            tmp_path,
            "--scope-type",
            "approved_draft",
            "--scope-id",
            "DRAFT-OPP-KABUKICHO-001",
            "--handoff-id",
            "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
            "--decision-status",
            "approved",
            "--execution-enabled",
            "true",
            "--approved-by",
            "human",
            "--reason",
            "Approved for one-shot autonomous execution under the current operational baseline.",
        )

        assert result.returncode == 0
        text = APPROVAL_MD.read_text(encoding="utf-8")
        assert "decision_status: approved" in text
        assert "execution_enabled: true" in text
    finally:
        _restore_approval(backup_json, backup_md)


def test_no_unrelated_runtime_files_changed(tmp_path: Path) -> None:
    marker = tmp_path / "sentinel.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("sentinel", encoding="utf-8")
    backup_json, backup_md = _backup_approval(tmp_path)
    try:
        result = _run(
            tmp_path,
            "--scope-type",
            "approved_draft",
            "--scope-id",
            "DRAFT-OPP-KABUKICHO-001",
            "--handoff-id",
            "REQ-DRAFT-DRAFT-OPP-KABUKICHO-001",
            "--decision-status",
            "approved",
            "--execution-enabled",
            "true",
            "--approved-by",
            "human",
            "--reason",
            "Approved for one-shot autonomous execution under the current operational baseline.",
        )

        assert result.returncode == 0
        assert marker.read_text(encoding="utf-8") == "sentinel"
    finally:
        _restore_approval(backup_json, backup_md)


def test_business_role_task_writes_to_per_scope_path_not_top_level(tmp_path: Path) -> None:
    business_id, role_id, task_id = "test_fixture_business", "market_research", "task-0001"
    fixture_scope_dir = scope_dir(business_id, role_id, task_id, REPO_ROOT)
    assert not fixture_scope_dir.exists(), "test fixture dir must not pre-exist in the real repo"
    top_level_before = APPROVAL_JSON.read_text(encoding="utf-8") if APPROVAL_JSON.exists() else None
    try:
        result = _run(
            tmp_path,
            "--scope-type",
            "business_role_task",
            "--scope-id",
            f"{business_id}:{role_id}:{task_id}",
            "--handoff-id",
            "REQ-TEST-FIXTURE-BUSINESS-MARKET-RESEARCH-TASK-0001",
            "--decision-status",
            "approved",
            "--execution-enabled",
            "true",
            "--approved-by",
            "human",
            "--reason",
            "test",
        )

        assert result.returncode == 0, result.stderr
        assert (fixture_scope_dir / "approval.json").exists()
        payload = json.loads((fixture_scope_dir / "approval.json").read_text(encoding="utf-8"))
        assert payload["scope_id"] == f"{business_id}:{role_id}:{task_id}"
        # must not touch the top-level legacy approval file
        top_level_after = APPROVAL_JSON.read_text(encoding="utf-8") if APPROVAL_JSON.exists() else None
        assert top_level_after == top_level_before
    finally:
        shutil.rmtree(REPO_ROOT / "system" / "runtime" / "agent_handoff" / "scopes" / business_id, ignore_errors=True)
