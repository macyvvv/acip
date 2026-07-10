from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import json

from system.core.business_agent_automation_control import automation_pause_info, is_automation_paused, resume_automation
from system.core.business_agent_handoff import load_business_agent_handoff, scope_dir
from system.core.business_agent_task_queue import _queue_path, load_queue

REPO_ROOT = Path(__file__).resolve().parents[2]
PAUSE_SCRIPT = REPO_ROOT / "system" / "scripts" / "business_agent" / "pause_automation.py"
RESUME_SCRIPT = REPO_ROOT / "system" / "scripts" / "business_agent" / "resume_automation.py"
PROPOSE_SCRIPT = REPO_ROOT / "system" / "scripts" / "business_agent" / "propose_task.py"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)


def test_pause_then_resume_round_trip_leaves_no_trace() -> None:
    # These scripts always resolve to the real repo root (matching
    # set_execution_approval.py's existing pattern), so this test operates
    # on the real repo's sentinel file -- verify it's completely absent
    # before and after, so this never leaves the real repo paused.
    assert is_automation_paused(REPO_ROOT) is False, "repo must not already be paused before this test runs"

    pause_result = _run(PAUSE_SCRIPT, "--reason", "test run", "--paused-by", "pytest")
    assert pause_result.returncode == 0, pause_result.stderr
    assert is_automation_paused(REPO_ROOT) is True
    info = automation_pause_info(REPO_ROOT)
    assert info["reason"] == "test run"
    assert info["paused_by"] == "pytest"

    resume_result = _run(RESUME_SCRIPT)
    assert resume_result.returncode == 0, resume_result.stderr
    assert "was_paused=true" in resume_result.stdout
    assert is_automation_paused(REPO_ROOT) is False


def test_resume_when_not_paused_is_a_safe_no_op() -> None:
    assert is_automation_paused(REPO_ROOT) is False
    result = _run(RESUME_SCRIPT)
    assert result.returncode == 0
    assert "was_paused=false" in result.stdout
    assert is_automation_paused(REPO_ROOT) is False


def test_manual_propose_task_still_works_while_automation_paused() -> None:
    # The pause is scoped to auto-*proposal* only (business_agent_trigger.py) --
    # an explicit human action via propose_task.py must never be blocked by it.
    # propose_task.py validates business_id against the real registry, so this
    # uses a real business_id with a clearly-fake, unique task_id fixture.
    business_id, role_id, task_id = "kabukicho_survival_map", "market_research", "task-pause-test-fixture"
    fixture_dir = scope_dir(business_id, role_id, task_id, REPO_ROOT)
    assert not fixture_dir.exists(), "test fixture must not pre-exist in the real repo"
    try:
        pause_result = _run(PAUSE_SCRIPT, "--reason", "test run", "--paused-by", "pytest")
        assert pause_result.returncode == 0, pause_result.stderr

        propose_result = _run(
            PROPOSE_SCRIPT,
            "--business-id", business_id,
            "--role-id", role_id,
            "--task-id", task_id,
            "--title", "manual propose while paused",
        )
        assert propose_result.returncode == 0, propose_result.stderr
        handoff = load_business_agent_handoff(business_id, role_id, task_id, REPO_ROOT)
        assert handoff is not None
        assert handoff["business_id"] == business_id
    finally:
        # Surgical cleanup only -- business_id (kabukicho_survival_map) has a
        # real, separately-pending scope (market_research/task-0001); must not
        # touch anything but this test's own fixture task_id.
        resume_automation(REPO_ROOT)
        shutil.rmtree(fixture_dir, ignore_errors=True)
        queue = [
            item for item in load_queue(REPO_ROOT)
            if not (item.get("business_id") == business_id and item.get("task_id") == task_id)
        ]
        _queue_path(REPO_ROOT).write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
