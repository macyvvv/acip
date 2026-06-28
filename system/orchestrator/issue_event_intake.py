from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.event_contract import EventContract, EventSource


@dataclass(frozen=True)
class IssueEventIntakeResult:
    event: EventContract
    eligible_for_resolution: bool


class IssueEventIntake:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def read_fixture(self, path: str | Path) -> EventContract:
        fixture_path = Path(path)
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        event = EventContract(
            event_id=str(data["event_id"]),
            source=EventSource.issue,
            issue_id=int(data["issue_id"]),
            pack_id=str(data.get("pack_id", "")) or None,
            ep_id=str(data.get("ep_id", "")) or None,
            marker_path=None,
            actor=str(data.get("actor", "Codex")),
            timestamp=str(data.get("timestamp", "")),
            action=str(data.get("action", "issue_event")),
            risk_level=str(data.get("risk_level", "low")),
            approval_required=bool(data.get("approval_required", False)),
            title=str(data.get("title", "")),
            body_summary=str(data.get("body_summary", "")),
            state=str(data.get("state", "")),
        )
        event.validate()
        return event

    def intake(self, path: str | Path) -> IssueEventIntakeResult:
        event = self.read_fixture(path)
        return IssueEventIntakeResult(event=event, eligible_for_resolution=event.state.lower() in {"open", "ready"})
