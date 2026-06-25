from __future__ import annotations

from orchestrator.implementation_planner import ImplementationPlanner
from orchestrator.specification_generator import ImplementationSpecification


def test_implementation_planner_generates_plan() -> None:
    planner = ImplementationPlanner(".")
    specification = ImplementationSpecification(
        spec_id="SPEC-REQ-0001",
        title="Specification for build",
        architecture_option_id="ARCH-REQ-0001",
        implementation_spec="Implement build",
        file_changeset=("a.py",),
        validation=("python scripts/validate_all.py",),
        rollback=("Revert a.py",),
        worker_instructions=("Keep the specification deterministic.",),
        specs_reference=("specs/EP-0139",),
    )
    plan = planner.plan(specification)
    assert plan.worker_candidate == "Codex"
    assert plan.execution_request.worker_assignment == "Codex"
    assert plan.approval_required is False
