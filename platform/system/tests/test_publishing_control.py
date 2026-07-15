from __future__ import annotations

from pathlib import Path

from system.core.business_agent_automation_control import is_automation_paused, pause_automation
from system.core.publishing_control import (
    is_publishing_paused,
    pause_publishing,
    publishing_pause_info,
    resume_publishing,
)


def test_not_paused_by_default(tmp_path: Path) -> None:
    assert is_publishing_paused(tmp_path) is False
    assert publishing_pause_info(tmp_path) is None


def test_pause_then_is_paused(tmp_path: Path) -> None:
    pause_publishing("suspicious note.com draft", "macy", tmp_path)
    assert is_publishing_paused(tmp_path) is True
    info = publishing_pause_info(tmp_path)
    assert info["reason"] == "suspicious note.com draft"
    assert info["paused_by"] == "macy"
    assert info["paused"] is True


def test_resume_clears_pause(tmp_path: Path) -> None:
    pause_publishing("reason", "macy", tmp_path)
    assert resume_publishing(tmp_path) is True
    assert is_publishing_paused(tmp_path) is False


def test_resume_when_not_paused_returns_false(tmp_path: Path) -> None:
    assert resume_publishing(tmp_path) is False


def test_publishing_switch_independent_of_automation_switch(tmp_path: Path) -> None:
    pause_publishing("only publishing needs to stop", "macy", tmp_path)
    assert is_publishing_paused(tmp_path) is True
    assert is_automation_paused(tmp_path) is False

    resume_publishing(tmp_path)
    pause_automation("only task auto-proposal needs to stop", "macy", tmp_path)
    assert is_automation_paused(tmp_path) is True
    assert is_publishing_paused(tmp_path) is False
