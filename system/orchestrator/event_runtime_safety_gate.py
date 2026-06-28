from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.event_contract import EventContract
from system.orchestrator.event_to_queue_resolver import EventResolution


@dataclass(frozen=True)
class EventSafetyDecision:
    approved: bool
    reason: str


class EventRuntimeSafetyGate:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def allow(self, event: EventContract, resolution: EventResolution) -> bool:
        if event.risk_level == "high" or event.approval_required:
            approved = False
            reason = "high risk requires approval"
        elif resolution.decision == "approval_hold":
            approved = False
            reason = "approval hold"
        else:
            approved = True
            reason = "approved for dry run only"
        runtime_dir = self.base_path / "runtime" / "event_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / "safety_gate.json").write_text(json.dumps({"approved": approved, "reason": reason}, indent=2), encoding="utf-8")
        return approved
