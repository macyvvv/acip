from __future__ import annotations

from system.orchestrator.event_contract import EventContract, EventSource


def test_event_contract_validates_issue_event() -> None:
    event = EventContract(
        event_id="evt-1",
        source=EventSource.issue,
        issue_id=13,
        pack_id="PACK-0005",
        ep_id="EP-0161",
        marker_path=None,
        actor="Codex",
        timestamp="2026-06-26T00:00:00Z",
        action="issue_event",
        risk_level="low",
        approval_required=False,
    )
    event.validate()
