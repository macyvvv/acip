from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import hashlib


@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    objective: str
    context: str
    constraints: tuple[str, ...]
    value_type: str
    acceptance_criteria: tuple[str, ...]
    risk: str
    approval_required: bool
    source: str


class RequirementIntakeError(ValueError):
    pass


class RequirementIntake:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def normalize(self, text: str, source: str = "conversation") -> Requirement:
        objective = text.strip()
        if not objective:
            raise RequirementIntakeError("Requirement text cannot be empty")
        requirement_id = self._stable_requirement_id(objective)
        value_type = self._infer_value_type(objective)
        risk = "medium" if any(word in objective.lower() for word in ("migrate", "delete", "destroy")) else "low"
        approval_required = risk != "low"
        return Requirement(
            requirement_id=requirement_id,
            objective=objective,
            context="",
            constraints=(),
            value_type=value_type,
            acceptance_criteria=(objective,),
            risk=risk,
            approval_required=approval_required,
            source=source,
        )

    def write_runtime_requirement(self, requirement: Requirement) -> None:
        runtime_dir = self.base_path / "runtime" / "solution" / "requirements"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "requirement_id": requirement.requirement_id,
            "objective": requirement.objective,
            "context": requirement.context,
            "constraints": list(requirement.constraints),
            "value_type": requirement.value_type,
            "acceptance_criteria": list(requirement.acceptance_criteria),
            "risk": requirement.risk,
            "approval_required": requirement.approval_required,
            "source": requirement.source,
        }
        (runtime_dir / "requirement.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _infer_value_type(self, objective: str) -> str:
        text = objective.lower()
        if any(word in text for word in ("revenue", "sales", "customer", "business")):
            return "business"
        if any(word in text for word in ("risk", "ops", "operational", "deploy")):
            return "operational"
        if any(word in text for word in ("learn", "research", "study")):
            return "learning"
        return "strategic"

    def _stable_requirement_id(self, objective: str) -> str:
        digest = hashlib.sha1(objective.encode("utf-8")).hexdigest()[:8]
        return f"REQ-{digest.upper()}"
