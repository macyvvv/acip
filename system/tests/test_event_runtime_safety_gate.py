from __future__ import annotations

from system.orchestrator.event_contract import EventContract, EventSource
from system.orchestrator.event_runtime_safety_gate import EventRuntimeSafetyGate
from system.orchestrator.event_to_queue_resolver import EventResolution


def test_event_runtime_safety_gate_blocks_high_risk(tmp_path) -> None:
    gate = EventRuntimeSafetyGate(tmp_path)
    event = EventContract(
        event_id="evt-1",
        source=EventSource.completion_marker,
        issue_id=9,
        pack_id="PACK-0005",
        ep_id="EP-0166",
        marker_path="system/runtime/handoff/latest.json",
        actor="Codex",
        timestamp="2026-06-26T00:00:00Z",
        action="completion_marker_update",
        risk_level="high",
        approval_required=True,
    )
    allowed = gate.allow(event, EventResolution(event_id="evt-1", decision="approval_hold", next_queue_item=None, approval_required=True, reason="hold"))
    assert allowed is False
