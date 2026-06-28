from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.event_contract import EventContract, EventSource


@dataclass(frozen=True)
class GitHubActionsEventFixture:
    event: EventContract


class GitHubActionsEventFixtureReader:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def read(self, path: str | Path) -> GitHubActionsEventFixture:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        event = EventContract(
            event_id=str(data["event_id"]),
            source=EventSource.manual_fixture,
            issue_id=int(data.get("issue_id") or 0) or None,
            pack_id=str(data.get("pack_id") or "") or None,
            ep_id=str(data.get("ep_id") or "") or None,
            marker_path=None,
            actor=str(data.get("actor", "Codex")),
            timestamp=str(data.get("timestamp", "")),
            action=str(data.get("action", "manual_fixture")),
            risk_level=str(data.get("risk_level", "low")),
            approval_required=bool(data.get("approval_required", False)),
        )
        event.validate()
        return GitHubActionsEventFixture(event=event)
