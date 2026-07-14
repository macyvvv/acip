from __future__ import annotations

from pathlib import Path

from system.core.scheduled_execution_control import is_scheduled_execution_paused, pause_scheduled_execution
from system.core.scheduled_merge_control import (
    is_scheduled_merge_paused,
    pause_scheduled_merge,
    resume_scheduled_merge,
    scheduled_merge_pause_info,
)


def test_not_paused_by_default(tmp_path: Path) -> None:
    assert is_scheduled_merge_paused(tmp_path) is False
    assert scheduled_merge_pause_info(tmp_path) is None


def test_pause_then_is_paused(tmp_path: Path) -> None:
    pause_scheduled_merge("investigating a suspect auto-merge", "macy", tmp_path)
    assert is_scheduled_merge_paused(tmp_path) is True
    info = scheduled_merge_pause_info(tmp_path)
    assert info["reason"] == "investigating a suspect auto-merge"
    assert info["paused_by"] == "macy"
    assert info["paused"] is True


def test_resume_clears_pause(tmp_path: Path) -> None:
    pause_scheduled_merge("reason", "macy", tmp_path)
    assert resume_scheduled_merge(tmp_path) is True
    assert is_scheduled_merge_paused(tmp_path) is False


def test_resume_when_not_paused_returns_false(tmp_path: Path) -> None:
    assert resume_scheduled_merge(tmp_path) is False


def test_independent_of_generation_kill_switch(tmp_path: Path) -> None:
    # Pausing merge must not affect whether the wake itself attempts
    # generation -- ADR-0040's whole premise is that these are two distinct
    # operator concerns with two distinct switches.
    pause_scheduled_merge("only merging needs to stop", "macy", tmp_path)
    assert is_scheduled_merge_paused(tmp_path) is True
    assert is_scheduled_execution_paused(tmp_path) is False

    resume_scheduled_merge(tmp_path)
    pause_scheduled_execution("only generation needs to stop", "macy", tmp_path)
    assert is_scheduled_execution_paused(tmp_path) is True
    assert is_scheduled_merge_paused(tmp_path) is False
