from __future__ import annotations

from orchestrator.architecture_planner import ArchitecturePlanner
from orchestrator.requirement_intake import Requirement


def test_architecture_planner_generates_option() -> None:
    planner = ArchitecturePlanner(".")
    requirement = Requirement(
        requirement_id="REQ-0001",
        objective="Build the pack",
        context="",
        constraints=(),
        value_type="strategic",
        acceptance_criteria=("done",),
        risk="low",
        approval_required=False,
        source="user",
    )
    options = planner.generate(requirement)
    assert options[0].option_id == "ARCH-req-0001"
