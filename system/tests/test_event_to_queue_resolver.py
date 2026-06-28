from __future__ import annotations

from system.orchestrator.event_contract import EventContract, EventSource
from system.orchestrator.event_to_queue_resolver import EventToQueueResolver


def test_event_to_queue_resolver_selects_next_queue_item(tmp_path) -> None:
    (tmp_path / "queue" / "READY").mkdir(parents=True)
    (tmp_path / "queue" / "READY" / "EP-9999-sample.md").write_text("pack_id: PACK-0005\nobjective: Sample\nstatus: READY\n", encoding="utf-8")
    event = EventContract(
        event_id="evt-1",
        source=EventSource.issue,
        issue_id=14,
        pack_id="PACK-0005",
        ep_id="EP-0164",
        marker_path=None,
        actor="Codex",
        timestamp="2026-06-26T00:00:00Z",
        action="issue_event",
        risk_level="low",
        approval_required=False,
    )
    resolution = EventToQueueResolver(tmp_path).resolve(event)
    assert resolution.decision == "queue_next_work"
    assert resolution.next_queue_item.endswith("EP-9999-sample.md")
