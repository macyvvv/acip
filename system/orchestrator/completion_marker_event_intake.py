from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.event_contract import EventContract, EventSource


@dataclass(frozen=True)
class CompletionMarkerEventIntakeResult:
    event: EventContract
    ready_for_review: bool


class CompletionMarkerEventIntake:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def read_latest(self) -> EventContract:
        payload = json.loads((self.base_path / "runtime" / "handoff" / "latest.json").read_text(encoding="utf-8"))
        event = EventContract(
            event_id=f"completion-{payload['pack_id']}",
            source=EventSource.completion_marker,
            issue_id=int(payload["parent_issue"]),
            pack_id=str(payload["pack_id"]),
            ep_id=str(payload["ep_id"]),
            marker_path="runtime/handoff/latest.json",
            actor="Codex",
            timestamp="2026-06-26T00:00:00Z",
            action="completion_marker_update",
            risk_level="low" if payload.get("requires_human_approval") is False else "medium",
            approval_required=bool(payload.get("requires_human_approval", False)),
            body_summary=f"validation_result: {payload['validation_result']}",
        )
        event.validate()
        return event

    def intake(self) -> CompletionMarkerEventIntakeResult:
        event = self.read_latest()
        return CompletionMarkerEventIntakeResult(event=event, ready_for_review=not event.approval_required)
