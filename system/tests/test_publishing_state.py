from __future__ import annotations

from pathlib import Path

import pytest

from system.core.publishing_state import (
    PublishingStateError,
    counts_for_today,
    counts_for_week,
    is_already_published,
    record_publish,
)


def test_not_published_by_default(tmp_path: Path) -> None:
    assert is_already_published("text_syndicate", "x", "marketing", "task-0001", tmp_path) is False
    assert counts_for_today("text_syndicate", "x", tmp_path) == 0
    assert counts_for_week("text_syndicate", "x", tmp_path) == 0


def test_record_publish_marks_dedup_and_increments_counters(tmp_path: Path) -> None:
    record_publish("text_syndicate", "marketing", "task-0001", "x", "dry_run", None, tmp_path)
    assert is_already_published("text_syndicate", "x", "marketing", "task-0001", tmp_path) is True
    assert counts_for_today("text_syndicate", "x", tmp_path) == 1
    assert counts_for_week("text_syndicate", "x", tmp_path) == 1


def test_double_publish_raises_not_double_increments(tmp_path: Path) -> None:
    record_publish("text_syndicate", "marketing", "task-0001", "x", "dry_run", None, tmp_path)
    with pytest.raises(PublishingStateError):
        record_publish("text_syndicate", "marketing", "task-0001", "x", "dry_run", None, tmp_path)
    assert counts_for_today("text_syndicate", "x", tmp_path) == 1


def test_sharded_per_business_and_platform(tmp_path: Path) -> None:
    record_publish("text_syndicate", "marketing", "task-0001", "x", "dry_run", None, tmp_path)
    assert is_already_published("text_syndicate", "threads", "marketing", "task-0001", tmp_path) is False
    assert is_already_published("kabukicho_survival_map", "x", "marketing", "task-0001", tmp_path) is False
    assert counts_for_today("text_syndicate", "threads", tmp_path) == 0
    assert counts_for_today("kabukicho_survival_map", "x", tmp_path) == 0


def test_corrupted_state_file_hard_fails(tmp_path: Path) -> None:
    path = tmp_path / "system/runtime/publishing/state/text_syndicate/x/state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json")
    with pytest.raises(PublishingStateError):
        is_already_published("text_syndicate", "x", "marketing", "task-0001", tmp_path)
    with pytest.raises(PublishingStateError):
        record_publish("text_syndicate", "marketing", "task-0002", "x", "dry_run", None, tmp_path)
