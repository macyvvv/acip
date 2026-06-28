from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.architecture_planner import ArchitecturePlanner
from system.orchestrator.implementation_planner import ImplementationPlanner
from system.orchestrator.pack_manager import PackManager
from system.orchestrator.requirement_intake import RequirementIntake
from system.orchestrator.review_release_planner import ReviewReleasePlanner
from system.orchestrator.specification_generator import SpecificationGenerator


@dataclass(frozen=True)
class SolutionDevelopmentRuntimeResult:
    pack_id: str
    requirement_id: str
    architecture_option_id: str
    specification_id: str
    implementation_plan_id: str
    review_release_plan_id: str
    next_action: str


class SolutionDevelopmentRuntimeError(ValueError):
    pass


class SolutionDevelopmentRuntime:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self, requirement_text: str) -> SolutionDevelopmentRuntimeResult:
        packs = PackManager(self.base_path).load_registry()
        pack = next((item for item in packs if item.pack_id == "PACK-0001"), None)
        if pack is None:
            raise SolutionDevelopmentRuntimeError("PACK-0001 is not registered")

        intake = RequirementIntake(self.base_path)
        requirement = intake.normalize(requirement_text)
        intake.write_runtime_requirement(requirement)

        architecture_planner = ArchitecturePlanner(self.base_path)
        architecture_option = architecture_planner.generate(requirement)[0]
        architecture_planner.write_runtime_architecture((architecture_option,))

        specification_generator = SpecificationGenerator(self.base_path)
        specification = specification_generator.generate(architecture_option)
        specification_generator.write_runtime_specification(specification)

        implementation_planner = ImplementationPlanner(self.base_path)
        implementation_plan = implementation_planner.plan(specification)
        implementation_planner.write_runtime_plan(implementation_plan)

        review_release_planner = ReviewReleasePlanner(self.base_path)
        review_release_plan = review_release_planner.plan(implementation_plan)
        review_release_planner.write_runtime_review_release(review_release_plan)

        runtime_dir = self.base_path / "runtime" / "solution" / "solution_runtime_state"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "pack_id": pack.pack_id,
            "requirement_id": requirement.requirement_id,
            "architecture_option_id": architecture_option.option_id,
            "specification_id": specification.spec_id,
            "implementation_plan_id": implementation_plan.plan_id,
            "review_release_plan_id": review_release_plan.plan_id,
            "next_action": review_release_plan.release_readiness,
        }
        (runtime_dir / "solution_runtime_state.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "SOLUTION_RUNTIME_STATE.md").write_text(
            "\n".join(
                [
                    "# SOLUTION_RUNTIME_STATE",
                    "",
                    f"pack_id: {pack.pack_id}",
                    f"requirement_id: {requirement.requirement_id}",
                    f"next_action: {review_release_plan.release_readiness}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return SolutionDevelopmentRuntimeResult(
            pack_id=pack.pack_id,
            requirement_id=requirement.requirement_id,
            architecture_option_id=architecture_option.option_id,
            specification_id=specification.spec_id,
            implementation_plan_id=implementation_plan.plan_id,
            review_release_plan_id=review_release_plan.plan_id,
            next_action=review_release_plan.release_readiness,
        )
