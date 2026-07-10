from __future__ import annotations

import json
from pathlib import Path

from system.core.agent_execution_approval import load_latest_handoff
from system.core.business_agent_handoff import write_business_agent_handoff
from system.core.business_agent_task_queue import load_queue
from system.core.business_agent_trigger import evaluate_and_enqueue_next_tasks


def _write_approval(path: Path, **overrides) -> None:
    payload = {
        "approval_id": "APP-1",
        "handoff_id": "REQ-SOME-HANDOFF",
        "scope_type": "business_role_task",
        "scope_id": "some:scope:id",
        "decision_status": "approved",
        "approved_by": "Human",
        "approved_at": "2026-07-10T00:00:00+00:00",
        "reason": "test",
        "execution_enabled": True,
        "supersedes": None,
    }
    payload.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def test_no_next_roles_returns_empty(tmp_path: Path) -> None:
    # doc_creation has next_roles == () for Level 1
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "doc_creation", "task-0001", "artifact.md", tmp_path)
    assert result == []


def test_market_research_success_enqueues_marketing(tmp_path: Path) -> None:
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    assert len(result) == 1
    assert result[0]["role_id"] == "marketing"
    queue = load_queue(tmp_path)
    assert len(queue) == 1
    assert queue[0]["business_id"] == "text_syndicate"
    assert queue[0]["role_id"] == "marketing"
    assert queue[0]["source"] == "auto_trigger"


def test_activates_when_nothing_else_is_pending(tmp_path: Path) -> None:
    # No prior handoff/approval at all -- safe to activate immediately.
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    assert result[0]["activated"] is True
    handoff = load_latest_handoff(tmp_path)
    assert handoff["business_id"] == "text_syndicate"
    assert handoff["role_id"] == "marketing"


def test_activates_when_current_handoff_is_the_just_completed_task(tmp_path: Path) -> None:
    # The handoff slot holds the task that JUST ran (market_research/task-0001)
    # and its approval is still marked approved (nothing invalidates it
    # post-run) -- this must NOT be treated as "someone else's pending scope."
    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc", tmp_path)
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        handoff_id="REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001",
        scope_id="text_syndicate:market_research:task-0001",
    )
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    assert result[0]["activated"] is True


def test_skips_activation_but_still_enqueues_when_a_different_scope_is_pending(tmp_path: Path) -> None:
    # A DIFFERENT business's task is currently approved and not yet executed --
    # activating the new one would silently clobber it.
    write_business_agent_handoff("kabukicho_survival_map", "marketing", "task-0007", "desc", tmp_path)
    _write_approval(
        tmp_path / "system" / "runtime" / "agent_handoff" / "approval.json",
        handoff_id="REQ-KABUKICHO-SURVIVAL-MAP-MARKETING-TASK-0007",
        scope_id="kabukicho_survival_map:marketing:task-0007",
    )
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    assert result[0]["activated"] is False
    # still enqueued, just not activated
    queue = load_queue(tmp_path)
    assert len(queue) == 1
    assert queue[0]["role_id"] == "marketing"
    # the other business's handoff must not have been touched
    handoff = load_latest_handoff(tmp_path)
    assert handoff["business_id"] == "kabukicho_survival_map"


def test_auto_task_ids_are_unique_and_sequential(tmp_path: Path) -> None:
    evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0002", "artifact.md", tmp_path)
    queue = load_queue(tmp_path)
    marketing_tasks = [item for item in queue if item["role_id"] == "marketing"]
    assert len(marketing_tasks) == 2
    assert {item["task_id"] for item in marketing_tasks} == {"auto-0001", "auto-0002"}


def test_analytics_success_enqueues_pdca(tmp_path: Path) -> None:
    result = evaluate_and_enqueue_next_tasks("somia", "analytics", "task-0001", "artifact.json", tmp_path)
    assert len(result) == 1
    assert result[0]["role_id"] == "pdca"
