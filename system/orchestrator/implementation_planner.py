from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.capability_router import CapabilityRouter
from orchestrator.execution_request import ExecutionRequest, ExecutionRequestBuilder
from orchestrator.specification_generator import ImplementationSpecification


@dataclass(frozen=True)
class ImplementationPlan:
    plan_id: str
    specification_id: str
    required_capability: str
    worker_candidate: str
    execution_request: ExecutionRequest
    approval_required: bool
    risk_level: str
    dependencies: tuple[str, ...]


class ImplementationPlannerError(ValueError):
    pass


class ImplementationPlanner:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def plan(self, specification: ImplementationSpecification) -> ImplementationPlan:
        required_capability = self._infer_required_capability(specification)
        route = CapabilityRouter(self.base_path).route(
            planner=self._planner_proxy(specification.spec_id),
            required_capabilities=(required_capability,),
            prohibited_actions=("approve", "deploy", "push_directly_to_main"),
            required_validation_responsibility=("run_repository_validation",),
            execution_boundary=("push_directly_to_main",),
        )
        approval_required = any("approval" in item.lower() for item in specification.worker_instructions)
        request = ExecutionRequestBuilder(self.base_path).from_governor_candidate(
            specification.spec_id,
            request_priority=100,
            approval_required=approval_required,
            dependency=specification.specs_reference,
            worker_assignment=route.worker_name,
        )
        return ImplementationPlan(
            plan_id=f"PLAN-{specification.spec_id.lower()}",
            specification_id=specification.spec_id,
            required_capability=required_capability,
            worker_candidate=route.worker_name,
            execution_request=request,
            approval_required=approval_required,
            risk_level=self._risk_from_specification(specification),
            dependencies=specification.specs_reference,
        )

    def write_runtime_plan(self, plan: ImplementationPlan) -> None:
        runtime_dir = self.base_path / "runtime" / "solution" / "implementation"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "plan_id": plan.plan_id,
            "specification_id": plan.specification_id,
            "required_capability": plan.required_capability,
            "worker_candidate": plan.worker_candidate,
            "execution_request": {
                "request_id": plan.execution_request.request_id,
                "request_status": plan.execution_request.request_status,
                "request_priority": plan.execution_request.request_priority,
                "approval_required": plan.execution_request.approval_required,
                "dependency": list(plan.execution_request.dependency),
                "worker_assignment": plan.execution_request.worker_assignment,
            },
            "approval_required": plan.approval_required,
            "risk_level": plan.risk_level,
            "dependencies": list(plan.dependencies),
        }
        (runtime_dir / "implementation_plan.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _infer_required_capability(self, specification: ImplementationSpecification) -> str:
        title = specification.title.lower()
        if "specification" in title:
            return "repository_implementation"
        raise ImplementationPlannerError("Unable to infer required capability")

    def _risk_from_specification(self, specification: ImplementationSpecification) -> str:
        text = " ".join(specification.worker_instructions).lower()
        if "destructive" in text:
            return "high"
        return "low"

    def _planner_proxy(self, spec_id: str):
        return type("PlannerProxy", (), {"next_ep": spec_id})()
