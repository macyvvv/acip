from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.event_contract import EventContract, EventSource


@dataclass(frozen=True)
class EventResolution:
    event_id: str
    decision: str
    next_queue_item: str | None
    approval_required: bool
    reason: str


class EventToQueueResolver:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def resolve(self, event: EventContract) -> EventResolution:
        if event.source == EventSource.completion_marker and event.approval_required:
            decision = "approval_hold"
            next_queue_item = None
            reason = "Completion marker requires human approval"
        else:
            next_item = self._next_queue_item()
            decision = "queue_next_work" if next_item else "no_work"
            next_queue_item = next_item
            reason = "Next queue item selected" if next_item else "No queue items available"
        payload = {
            "event_id": event.event_id,
            "decision": decision,
            "next_queue_item": next_queue_item,
            "approval_required": event.approval_required,
            "reason": reason,
        }
        runtime_dir = self.base_path / "runtime" / "event_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / "event_to_queue_resolution.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return EventResolution(event_id=event.event_id, decision=decision, next_queue_item=next_queue_item, approval_required=event.approval_required, reason=reason)

    def _next_queue_item(self) -> str | None:
        queue_dir = self.base_path / "queue" / "READY"
        items = sorted(queue_dir.glob("EP-*.md"))
        return str(items[0].relative_to(self.base_path)) if items else None
