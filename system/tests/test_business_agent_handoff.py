from __future__ import annotations

import json
from pathlib import Path

from system.core.business_agent_handoff import load_business_agent_handoff, scope_dir, write_business_agent_handoff


def test_writes_per_task_scoped_handoff(tmp_path: Path) -> None:
    handoff_path = write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "Research impression-driving niches", tmp_path)
    assert handoff_path == tmp_path / "system" / "runtime" / "agent_handoff" / "scopes" / "text_syndicate" / "market_research" / "task-0001" / "handoff.json"
    payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    assert payload["business_id"] == "text_syndicate"
    assert payload["role_id"] == "market_research"
    assert payload["task_id"] == "task-0001"
    assert payload["issue_number"] is None
    assert payload["approved_draft_id"] is None
    assert payload["request_id"] == "REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001"
    assert (scope_dir("text_syndicate", "market_research", "task-0001", tmp_path) / "handoff.md").exists()


def test_does_not_touch_top_level_legacy_handoff(tmp_path: Path) -> None:
    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc", tmp_path)
    assert not (tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json").exists()


def test_two_different_scopes_never_collide(tmp_path: Path) -> None:
    write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "desc A", tmp_path)
    write_business_agent_handoff("kabukicho_survival_map", "marketing", "task-0007", "desc B", tmp_path)
    a = load_business_agent_handoff("text_syndicate", "market_research", "task-0001", tmp_path)
    b = load_business_agent_handoff("kabukicho_survival_map", "marketing", "task-0007", tmp_path)
    assert a["business_id"] == "text_syndicate"
    assert b["business_id"] == "kabukicho_survival_map"


def test_load_business_agent_handoff_returns_none_when_missing(tmp_path: Path) -> None:
    assert load_business_agent_handoff("text_syndicate", "market_research", "task-9999", tmp_path) is None
