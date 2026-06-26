from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.event_runtime_dry_run import EventRuntimeDryRun


@dataclass(frozen=True)
class WorkflowDispatchRuntimeResult:
    dry_run_path: str
    decision: str
    next_queue_item: str | None


class WorkflowDispatchRuntime:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self, fixture_path: str | Path) -> WorkflowDispatchRuntimeResult:
        result = EventRuntimeDryRun(self.base_path).run_issue_fixture(fixture_path)
        payload = {
            "decision": result.resolution.decision,
            "next_queue_item": result.resolution.next_queue_item,
            "approved": result.approved,
        }
        runtime_dir = self.base_path / "runtime" / "event_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / "workflow_dispatch.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return WorkflowDispatchRuntimeResult(dry_run_path=result.dry_run_path, decision=result.resolution.decision, next_queue_item=result.resolution.next_queue_item)
