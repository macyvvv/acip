from __future__ import annotations

from system.core.business_agent_task_queue import add_task, load_queue, mark_task_status


def test_add_task_creates_candidate_entry(tmp_path) -> None:
    queue = add_task("text_syndicate", "market_research", "task-0001", "Research niches", tmp_path)
    assert len(queue) == 1
    assert queue[0]["status"] == "candidate"


def test_add_task_is_idempotent(tmp_path) -> None:
    add_task("text_syndicate", "market_research", "task-0001", "Research niches", tmp_path)
    queue = add_task("text_syndicate", "market_research", "task-0001", "Research niches (dup)", tmp_path)
    assert len(queue) == 1


def test_mark_task_status_updates_matching_entry(tmp_path) -> None:
    add_task("text_syndicate", "market_research", "task-0001", "Research niches", tmp_path)
    queue = mark_task_status("text_syndicate", "market_research", "task-0001", "approved", tmp_path)
    assert queue[0]["status"] == "approved"


def test_load_queue_empty_when_missing(tmp_path) -> None:
    assert load_queue(tmp_path) == []


def test_add_task_defaults_source_to_manual(tmp_path) -> None:
    queue = add_task("text_syndicate", "market_research", "task-0001", "Research niches", tmp_path)
    assert queue[0]["source"] == "manual"


def test_add_task_records_auto_trigger_source(tmp_path) -> None:
    queue = add_task("text_syndicate", "marketing", "auto-0001", "Auto-triggered", tmp_path, source="auto_trigger")
    assert queue[0]["source"] == "auto_trigger"
