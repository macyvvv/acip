from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.architecture_planner import ArchitectureOption


@dataclass(frozen=True)
class ImplementationSpecification:
    spec_id: str
    title: str
    architecture_option_id: str
    implementation_spec: str
    file_changeset: tuple[str, ...]
    validation: tuple[str, ...]
    rollback: tuple[str, ...]
    worker_instructions: tuple[str, ...]
    specs_reference: tuple[str, ...]


class SpecificationGeneratorError(ValueError):
    pass


class SpecificationGenerator:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def generate(self, option: ArchitectureOption) -> ImplementationSpecification:
        if not option.option_id:
            raise SpecificationGeneratorError("Architecture option id is required")
        spec_id = f"SPEC-{option.option_id.lower()}"
        return ImplementationSpecification(
            spec_id=spec_id,
            title=f"Specification for {option.title}",
            architecture_option_id=option.option_id,
            implementation_spec=f"Implement the architecture option {option.option_id} with deterministic repository changes.",
            file_changeset=(
                "orchestrator/specification_generator.py",
                "docs/current/SPECIFICATION_GENERATOR.md",
                "runtime/solution/specifications/specification.json",
                "specs/EP-0139",
            ),
            validation=(
                "python scripts/validate_all.py",
                "python -m pytest -q",
            ),
            rollback=("Revert the files listed in file_changeset.",),
            worker_instructions=(
                "Keep the specification deterministic.",
                "Do not introduce destructive changes.",
            ),
            specs_reference=("specs/EP-0138", "specs/EP-0139"),
        )

    def write_runtime_specification(self, specification: ImplementationSpecification) -> None:
        runtime_dir = self.base_path / "runtime" / "solution" / "specifications"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "spec_id": specification.spec_id,
            "title": specification.title,
            "architecture_option_id": specification.architecture_option_id,
            "implementation_spec": specification.implementation_spec,
            "file_changeset": list(specification.file_changeset),
            "validation": list(specification.validation),
            "rollback": list(specification.rollback),
            "worker_instructions": list(specification.worker_instructions),
            "specs_reference": list(specification.specs_reference),
        }
        (runtime_dir / "specification.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
