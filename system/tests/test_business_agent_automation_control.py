from __future__ import annotations

from pathlib import Path

from system.core.business_agent_automation_control import (
    automation_pause_info,
    is_automation_paused,
    pause_automation,
    resume_automation,
)


def test_not_paused_by_default(tmp_path: Path) -> None:
    assert is_automation_paused(tmp_path) is False
    assert automation_pause_info(tmp_path) is None


def test_pause_then_is_paused(tmp_path: Path) -> None:
    pause_automation("investigating an unexpected chain", "macy", tmp_path)
    assert is_automation_paused(tmp_path) is True
    info = automation_pause_info(tmp_path)
    assert info["reason"] == "investigating an unexpected chain"
    assert info["paused_by"] == "macy"
    assert info["paused"] is True


def test_resume_clears_pause(tmp_path: Path) -> None:
    pause_automation("reason", "macy", tmp_path)
    assert resume_automation(tmp_path) is True
    assert is_automation_paused(tmp_path) is False


def test_resume_when_not_paused_returns_false(tmp_path: Path) -> None:
    assert resume_automation(tmp_path) is False
