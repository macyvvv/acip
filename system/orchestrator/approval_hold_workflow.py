from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class ApprovalHoldDecision:
    hold: bool
    reason: str


class ApprovalHoldWorkflow:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def decide(self, approval_required: bool, risk_level: str) -> ApprovalHoldDecision:
        hold = approval_required or risk_level == "high"
        reason = "approval required" if hold else "no approval hold"
        runtime_dir = self.base_path / "runtime" / "event_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / "approval_hold.json").write_text(json.dumps({"hold": hold, "reason": reason}, indent=2), encoding="utf-8")
        return ApprovalHoldDecision(hold=hold, reason=reason)
