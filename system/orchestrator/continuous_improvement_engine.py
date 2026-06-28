from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.repository_governor import GovernorCandidate, RepositoryGovernor
from orchestrator.repository_state_manager import RepositoryStateManager


@dataclass(frozen=True)
class ImprovementCandidate:
    ep: str
    risk: str
    value: int
    required_capability: str
    approval_required: bool
    reason: str


@dataclass(frozen=True)
class ImprovementPlan:
    candidates: tuple[ImprovementCandidate, ...]


class ContinuousImprovementEngine:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def build_plan(self) -> ImprovementPlan:
        governor = RepositoryGovernor(self.base_path)
        state = RepositoryStateManager(self.base_path).build_state([])
        candidates = []
        for index, item in enumerate(governor.build_candidates(), start=1):
            value = 100 - (index * 10)
            if state.validation_status != "success":
                value -= 5
            candidates.append(
                ImprovementCandidate(
                    ep=item.ep,
                    risk=item.risk_level,
                    value=value,
                    required_capability=item.required_capability,
                    approval_required=item.human_approval_required,
                    reason=item.reason,
                )
            )
        return ImprovementPlan(candidates=tuple(sorted(candidates, key=lambda item: (-item.value, item.ep))))

    def write_runtime_candidates(self, plan: ImprovementPlan) -> None:
        runtime_dir = self.base_path / "runtime" / "improvement"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "candidates": [
                {
                    "ep": candidate.ep,
                    "risk": candidate.risk,
                    "value": candidate.value,
                    "required_capability": candidate.required_capability,
                    "approval_required": candidate.approval_required,
                    "reason": candidate.reason,
                }
                for candidate in plan.candidates
            ]
        }
        (runtime_dir / "improvement_candidates.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
