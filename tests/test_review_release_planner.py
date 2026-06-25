from __future__ import annotations

from orchestrator.implementation_planner import ImplementationPlan
from orchestrator.execution_request import ExecutionRequest
from orchestrator.review_release_planner import ReviewReleasePlanner


def test_review_release_planner_generates_plan() -> None:
    planner = ReviewReleasePlanner(".")
    implementation_plan = ImplementationPlan(
        plan_id="PLAN-SPEC-0001",
        specification_id="SPEC-0001",
        required_capability="repository_implementation",
        worker_candidate="Codex",
        execution_request=ExecutionRequest(
            request_id="REQ-SPEC-0001",
            request_status="ready",
            request_priority=100,
            approval_required=False,
            dependency=("specs/EP-0139",),
            worker_assignment="Codex",
        ),
        approval_required=False,
        risk_level="low",
        dependencies=("specs/EP-0139",),
    )
    plan = planner.plan(implementation_plan)
    assert plan.release_readiness == "ready"
    assert "python scripts/validate_all.py" in plan.validation_plan
