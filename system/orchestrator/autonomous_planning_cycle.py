from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import TYPE_CHECKING

from orchestrator.continuous_improvement_engine import ContinuousImprovementEngine
from orchestrator.human_approval_gate import HumanApprovalGate
from orchestrator.repository_governor import RepositoryGovernor
from orchestrator.repository_state_manager import RepositoryStateManager

if TYPE_CHECKING:
    from orchestrator.execution_kernel import ExecutionKernel


@dataclass(frozen=True)
class AutonomousPlanningCycleResult:
    repository_state: object
    governor_candidates: tuple[object, ...]
    improvement_candidates: tuple[object, ...]
    approvals_required: tuple[str, ...]
    execution_ready: tuple[str, ...]
    next_action: str


class AutonomousPlanningCycle:
    def __init__(self, kernel: ExecutionKernel, base_path: str | Path = ".") -> None:
        self.kernel = kernel
        self.base_path = Path(base_path)

    def run(self) -> AutonomousPlanningCycleResult:
        repository_state = RepositoryStateManager(self.base_path).build_state([])
        governor = RepositoryGovernor(self.base_path)
        governor_candidates = governor.build_candidates()
        improvement_plan = ContinuousImprovementEngine(self.base_path).build_plan()
        approvals_required = tuple(
            candidate.ep
            for candidate in improvement_plan.candidates
            if HumanApprovalGate(self.base_path).requires_approval(candidate)
        )
        execution_ready = tuple(
            candidate.ep for candidate in improvement_plan.candidates if candidate.ep not in approvals_required
        )
        next_action = (
            "await human approval"
            if approvals_required
            else self.kernel.run_validation_pipeline().next_action or "python scripts/validate_all.py"
        )
        return AutonomousPlanningCycleResult(
            repository_state=repository_state,
            governor_candidates=governor_candidates,
            improvement_candidates=improvement_plan.candidates,
            approvals_required=approvals_required,
            execution_ready=execution_ready,
            next_action=next_action,
        )

    def write_runtime_plan(self, result: AutonomousPlanningCycleResult) -> None:
        runtime_dir = self.base_path / "runtime" / "planning"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "approvals_required": list(result.approvals_required),
            "execution_ready": list(result.execution_ready),
            "next_action": result.next_action,
        }
        (runtime_dir / "autonomous_plan.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
