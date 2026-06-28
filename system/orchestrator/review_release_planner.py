from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.implementation_planner import ImplementationPlan


@dataclass(frozen=True)
class ReviewReleasePlan:
    plan_id: str
    implementation_plan_id: str
    review_checklist: tuple[str, ...]
    validation_plan: tuple[str, ...]
    release_readiness: str
    rollback_requirement: tuple[str, ...]
    journal_entry: tuple[str, ...]


class ReviewReleasePlannerError(ValueError):
    pass


class ReviewReleasePlanner:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def plan(self, implementation_plan: ImplementationPlan) -> ReviewReleasePlan:
        if not implementation_plan.plan_id:
            raise ReviewReleasePlannerError("Implementation plan id is required")
        release_readiness = "ready" if not implementation_plan.approval_required else "pending_approval"
        return ReviewReleasePlan(
            plan_id=f"REVIEW-{implementation_plan.plan_id.lower()}",
            implementation_plan_id=implementation_plan.plan_id,
            review_checklist=(
                "Confirm implementation scope matches the specification.",
                "Confirm validation commands are present.",
                "Confirm rollback requirement is explicit.",
            ),
            validation_plan=(
                "python scripts/validate_all.py",
                "python -m pytest -q",
                *implementation_plan.execution_request.dependency,
            ),
            release_readiness=release_readiness,
            rollback_requirement=("Revert the implementation plan and generated artifacts.",),
            journal_entry=(
                f"implementation_plan_id: {implementation_plan.plan_id}",
                f"release_readiness: {release_readiness}",
            ),
        )

    def write_runtime_review_release(self, plan: ReviewReleasePlan) -> None:
        runtime_dir = self.base_path / "runtime" / "solution" / "review_release"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "plan_id": plan.plan_id,
            "implementation_plan_id": plan.implementation_plan_id,
            "review_checklist": list(plan.review_checklist),
            "validation_plan": list(plan.validation_plan),
            "release_readiness": plan.release_readiness,
            "rollback_requirement": list(plan.rollback_requirement),
            "journal_entry": list(plan.journal_entry),
        }
        (runtime_dir / "review_release_plan.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
