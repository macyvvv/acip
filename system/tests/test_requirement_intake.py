from __future__ import annotations

from system.orchestrator.requirement_intake import RequirementIntake


def test_requirement_intake_normalizes_text(tmp_path) -> None:
    base_path = tmp_path
    (base_path / "solution" / "requirements").mkdir(parents=True)
    intake = RequirementIntake(base_path)
    requirement = intake.normalize("Build a solution development pack", source="user")
    assert requirement.source == "user"
    assert requirement.objective.startswith("Build")
