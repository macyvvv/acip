from __future__ import annotations

from orchestrator.requirement_intake import RequirementIntake


def test_requirement_intake_normalizes_text() -> None:
    intake = RequirementIntake(".")
    requirement = intake.normalize("Build a solution development pack", source="user")
    assert requirement.source == "user"
    assert requirement.objective.startswith("Build")
