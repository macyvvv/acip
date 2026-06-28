from __future__ import annotations

from orchestrator.continuous_improvement_engine import ImprovementCandidate
from orchestrator.human_approval_gate import HumanApprovalGate


def test_human_approval_gate_requires_high_risk_approval() -> None:
    gate = HumanApprovalGate(".")
    candidate = ImprovementCandidate(
        ep="EP-9999",
        risk="high",
        value=1,
        required_capability="test",
        approval_required=False,
        reason="risk",
    )
    assert gate.requires_approval(candidate)
