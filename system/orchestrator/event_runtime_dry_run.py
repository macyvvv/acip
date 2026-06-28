from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.completion_marker_event_intake import CompletionMarkerEventIntake
from system.orchestrator.event_contract import EventContract
from system.orchestrator.event_to_queue_resolver import EventResolution, EventToQueueResolver
from system.orchestrator.issue_event_intake import IssueEventIntake
from system.orchestrator.event_runtime_safety_gate import EventRuntimeSafetyGate


@dataclass(frozen=True)
class EventRuntimeDryRunResult:
    event: EventContract
    resolution: EventResolution
    approved: bool
    dry_run_path: str


class EventRuntimeDryRun:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run_issue_fixture(self, fixture_path: str | Path) -> EventRuntimeDryRunResult:
        event = IssueEventIntake(self.base_path).read_fixture(fixture_path)
        return self._run(event)

    def run_completion_marker(self) -> EventRuntimeDryRunResult:
        event = CompletionMarkerEventIntake(self.base_path).read_latest()
        return self._run(event)

    def _run(self, event: EventContract) -> EventRuntimeDryRunResult:
        resolution = EventToQueueResolver(self.base_path).resolve(event)
        approved = EventRuntimeSafetyGate(self.base_path).allow(event, resolution)
        runtime_dir = self.base_path / "runtime" / "event_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "event_id": event.event_id,
            "source": event.source.value,
            "decision": resolution.decision,
            "next_queue_item": resolution.next_queue_item,
            "approved": approved,
            "approval_required": event.approval_required,
        }
        dry_run_path = runtime_dir / "dry_run.json"
        dry_run_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "dry_run.md").write_text("# EVENT_RUNTIME_DRY_RUN\n\nDeterministic event runtime dry-run output.\n", encoding="utf-8")
        return EventRuntimeDryRunResult(event=event, resolution=resolution, approved=approved, dry_run_path=str(dry_run_path))
