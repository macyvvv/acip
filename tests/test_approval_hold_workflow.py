from __future__ import annotations

from orchestrator.approval_hold_workflow import ApprovalHoldWorkflow


def test_approval_hold_workflow_blocks_high_risk(tmp_path) -> None:
    decision = ApprovalHoldWorkflow(tmp_path).decide(True, "high")
    assert decision.hold is True
