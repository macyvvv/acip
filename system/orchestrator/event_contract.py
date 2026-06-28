from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EventSource(str, Enum):
    issue = "issue"
    completion_marker = "completion_marker"
    manual_fixture = "manual_fixture"


@dataclass(frozen=True)
class EventContract:
    event_id: str
    source: EventSource
    issue_id: int | None
    pack_id: str | None
    ep_id: str | None
    marker_path: str | None
    actor: str
    timestamp: str
    action: str
    risk_level: str
    approval_required: bool
    title: str = ""
    body_summary: str = ""
    state: str = ""

    def validate(self) -> None:
        if not self.event_id:
            raise ValueError("Missing event_id")
        if self.source not in {EventSource.issue, EventSource.completion_marker, EventSource.manual_fixture}:
            raise ValueError("Invalid source")
        if self.source == EventSource.issue and self.issue_id is None:
            raise ValueError("Issue event requires issue_id")
        if self.source == EventSource.completion_marker and not self.marker_path:
            raise ValueError("Completion marker event requires marker_path")
        if self.risk_level not in {"low", "medium", "high"}:
            raise ValueError("Invalid risk_level")
