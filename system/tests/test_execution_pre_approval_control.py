from __future__ import annotations

from pathlib import Path

from system.core.business_agent_automation_control import is_automation_paused, pause_automation
from system.core.execution_pre_approval_control import (
    is_pre_approval_paused,
    pause_pre_approval,
    pre_approval_pause_info,
    resume_pre_approval,
)


def test_not_paused_by_default(tmp_path: Path) -> None:
    assert is_pre_approval_paused(tmp_path) is False
    assert pre_approval_pause_info(tmp_path) is None


def test_pause_then_is_paused(tmp_path: Path) -> None:
    pause_pre_approval("investigating a misconfigured policy", "macy", tmp_path)
    assert is_pre_approval_paused(tmp_path) is True
    info = pre_approval_pause_info(tmp_path)
    assert info["reason"] == "investigating a misconfigured policy"
    assert info["paused_by"] == "macy"
    assert info["paused"] is True


def test_resume_clears_pause(tmp_path: Path) -> None:
    pause_pre_approval("reason", "macy", tmp_path)
    assert resume_pre_approval(tmp_path) is True
    assert is_pre_approval_paused(tmp_path) is False


def test_resume_when_not_paused_returns_false(tmp_path: Path) -> None:
    assert resume_pre_approval(tmp_path) is False


def test_independent_of_automation_switch(tmp_path: Path) -> None:
    pause_pre_approval("only pre-approval needs to stop", "macy", tmp_path)
    assert is_pre_approval_paused(tmp_path) is True
    assert is_automation_paused(tmp_path) is False

    resume_pre_approval(tmp_path)
    pause_automation("only task auto-proposal needs to stop", "macy", tmp_path)
    assert is_automation_paused(tmp_path) is True
    assert is_pre_approval_paused(tmp_path) is False
