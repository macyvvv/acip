from __future__ import annotations

from pathlib import Path

from system.orchestrator.architecture_planner import ArchitecturePlanner
from system.orchestrator.requirement_intake import Requirement


def test_architecture_planner_generates_option(tmp_path: Path) -> None:
    base_path = tmp_path
    (base_path / "solution" / "architecture").mkdir(parents=True)
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
    planner = ArchitecturePlanner(base_path)
    options = planner.generate(requirement)
    assert options[0].option_id == "ARCH-req-0001"
