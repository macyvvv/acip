from __future__ import annotations

from pathlib import Path

from system.core.business_agent_automation_control import is_automation_paused, pause_automation
from system.core.execution_pre_approval_control import is_pre_approval_paused, pause_pre_approval
from system.core.scheduled_execution_control import (
    is_scheduled_execution_paused,
    pause_scheduled_execution,
    resume_scheduled_execution,
    scheduled_execution_pause_info,
)


def test_not_paused_by_default(tmp_path: Path) -> None:
    assert is_scheduled_execution_paused(tmp_path) is False
    assert scheduled_execution_pause_info(tmp_path) is None


def test_pause_then_is_paused(tmp_path: Path) -> None:
    pause_scheduled_execution("debugging a runaway loop", "macy", tmp_path)
    assert is_scheduled_execution_paused(tmp_path) is True
    info = scheduled_execution_pause_info(tmp_path)
    assert info["reason"] == "debugging a runaway loop"
    assert info["paused_by"] == "macy"
    assert info["paused"] is True


def test_resume_clears_pause(tmp_path: Path) -> None:
    pause_scheduled_execution("reason", "macy", tmp_path)
    assert resume_scheduled_execution(tmp_path) is True
    assert is_scheduled_execution_paused(tmp_path) is False


def test_resume_when_not_paused_returns_false(tmp_path: Path) -> None:
    assert resume_scheduled_execution(tmp_path) is False


def test_independent_of_sibling_switches(tmp_path: Path) -> None:
    # Pausing the scheduler must not affect Level 1/2's proposal-freeze switch
    # or Level 3a's pre-approval switch -- each of the 4 kill switches this
    # platform now has is independently scoped.
    pause_scheduled_execution("only the scheduler needs to stop", "macy", tmp_path)
    assert is_scheduled_execution_paused(tmp_path) is True
    assert is_automation_paused(tmp_path) is False
    assert is_pre_approval_paused(tmp_path) is False

    resume_scheduled_execution(tmp_path)
    pause_automation("only task auto-proposal needs to stop", "macy", tmp_path)
    assert is_automation_paused(tmp_path) is True
    assert is_scheduled_execution_paused(tmp_path) is False

    pause_pre_approval("only pre-approval needs to stop", "macy", tmp_path)
    assert is_pre_approval_paused(tmp_path) is True
    assert is_scheduled_execution_paused(tmp_path) is False
