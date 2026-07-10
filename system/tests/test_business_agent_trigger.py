from __future__ import annotations

from pathlib import Path

from system.core.business_agent_automation_control import pause_automation
from system.core.business_agent_handoff import load_business_agent_handoff
from system.core.business_agent_task_queue import load_queue
from system.core.business_agent_trigger import evaluate_and_enqueue_next_tasks


def test_no_next_roles_returns_empty(tmp_path: Path) -> None:
    # doc_creation has next_roles == () -- terminal
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


def test_always_activates_now_that_scopes_are_per_task(tmp_path: Path) -> None:
    # Level 2: no shared slot, so there is no "someone else's pending scope"
    # to avoid clobbering -- every enqueued task is activated.
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    assert result[0]["activated"] is True
    handoff = load_business_agent_handoff("text_syndicate", "marketing", result[0]["task_id"], tmp_path)
    assert handoff is not None
    assert handoff["business_id"] == "text_syndicate"
    assert handoff["role_id"] == "marketing"


def test_does_not_touch_other_businesses_scopes(tmp_path: Path) -> None:
    # A different business's pending scope must be completely untouched --
    # not because of a guard, but because per-task files never share a path.
    from system.core.business_agent_handoff import write_business_agent_handoff

    write_business_agent_handoff("kabukicho_survival_map", "marketing", "task-0007", "desc", tmp_path)
    evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)

    other = load_business_agent_handoff("kabukicho_survival_map", "marketing", "task-0007", tmp_path)
    assert other is not None
    assert other["business_id"] == "kabukicho_survival_map"


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


def test_pdca_loop_closes_back_to_market_research(tmp_path: Path) -> None:
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "pdca", "task-0001", "artifact.md", tmp_path)
    assert len(result) == 1
    assert result[0]["role_id"] == "market_research"
    assert result[0]["activated"] is True


def test_pdca_loop_and_content_chain_coexist_for_same_business(tmp_path: Path) -> None:
    # The exact scenario the per-task (not per-business) design decision was
    # made for: a business's content chain and its PDCA loop both have a
    # task pending at the same time, and neither clobbers the other.
    content_result = evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    pdca_result = evaluate_and_enqueue_next_tasks("text_syndicate", "pdca", "task-0001", "pdca-artifact.md", tmp_path)

    marketing_task_id = content_result[0]["task_id"]
    new_market_research_task_id = pdca_result[0]["task_id"]

    marketing_handoff = load_business_agent_handoff("text_syndicate", "marketing", marketing_task_id, tmp_path)
    market_research_handoff = load_business_agent_handoff("text_syndicate", "market_research", new_market_research_task_id, tmp_path)

    assert marketing_handoff is not None
    assert market_research_handoff is not None
    queue = load_queue(tmp_path)
    assert len(queue) == 2


def test_paused_automation_returns_empty_and_touches_nothing(tmp_path: Path) -> None:
    pause_automation("investigating", "macy", tmp_path)
    result = evaluate_and_enqueue_next_tasks("text_syndicate", "market_research", "task-0001", "artifact.md", tmp_path)
    assert result == []
    assert load_queue(tmp_path) == []
    assert load_business_agent_handoff("text_syndicate", "marketing", "auto-0001", tmp_path) is None
