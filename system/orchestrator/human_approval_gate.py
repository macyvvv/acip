from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.continuous_improvement_engine import ImprovementCandidate


@dataclass(frozen=True)
class ApprovalRecord:
    candidate_ep: str
    approved: bool
    approver: str
    reason: str


class HumanApprovalGate:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def requires_approval(self, candidate: ImprovementCandidate) -> bool:
        return candidate.approval_required or candidate.risk in {"high"}

    def approve(self, candidate: ImprovementCandidate, approver: str, reason: str) -> ApprovalRecord:
        record = ApprovalRecord(candidate_ep=candidate.ep, approved=True, approver=approver, reason=reason)
        self._write_record(record)
        return record

    def deny(self, candidate: ImprovementCandidate, approver: str, reason: str) -> ApprovalRecord:
        record = ApprovalRecord(candidate_ep=candidate.ep, approved=False, approver=approver, reason=reason)
        self._write_record(record)
        return record

    def _write_record(self, record: ApprovalRecord) -> None:
        runtime_dir = self.base_path / "runtime" / "approval"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "candidate_ep": record.candidate_ep,
            "approved": record.approved,
            "approver": record.approver,
            "reason": record.reason,
        }
        (runtime_dir / "approval_state.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
