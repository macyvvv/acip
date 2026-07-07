from __future__ import annotations

import json
from pathlib import Path

from system.core.business_agent_handoff import write_business_agent_handoff


def test_writes_canonical_single_slot_handoff(tmp_path: Path) -> None:
    handoff_path = write_business_agent_handoff("text_syndicate", "market_research", "task-0001", "Research impression-driving niches", tmp_path)
    assert handoff_path == tmp_path / "system" / "runtime" / "agent_handoff" / "latest.json"
    payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    assert payload["business_id"] == "text_syndicate"
    assert payload["role_id"] == "market_research"
    assert payload["task_id"] == "task-0001"
    assert payload["issue_number"] is None
    assert payload["approved_draft_id"] is None
    assert payload["request_id"] == "REQ-TEXT-SYNDICATE-MARKET-RESEARCH-TASK-0001"
    assert (tmp_path / "system" / "runtime" / "agent_handoff" / "latest.md").exists()
