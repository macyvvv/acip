from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.requirement_intake import Requirement


@dataclass(frozen=True)
class ArchitectureOption:
    option_id: str
    title: str
    tradeoff: str
    risk: str
    dependency: tuple[str, ...]
    affected_area: tuple[str, ...]
    adr_candidates: tuple[str, ...]
    wbs_candidates: tuple[str, ...]
    basis_references: tuple[str, ...]


class ArchitecturePlanner:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def generate(self, requirement: Requirement) -> tuple[ArchitectureOption, ...]:
        slug = requirement.requirement_id.lower()
        option = ArchitectureOption(
            option_id=f"ARCH-{slug}",
            title=f"Architecture for {requirement.objective}",
            tradeoff="Minimize implementation complexity while preserving determinism.",
            risk=requirement.risk,
            dependency=tuple(requirement.constraints),
            affected_area=("orchestrator", "docs/current", "runtime"),
            adr_candidates=("system/orchestrator/ADR-0001.md",),
            wbs_candidates=("system/orchestrator/WBS.md",),
            basis_references=("basis/PROJECT.md", "basis/REPOSITORY_CONVENTIONS.md"),
        )
        return (option,)

    def write_runtime_architecture(self, options: tuple[ArchitectureOption, ...]) -> None:
        runtime_dir = self.base_path / "runtime" / "solution" / "architecture"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "option_id": option.option_id,
                "title": option.title,
                "tradeoff": option.tradeoff,
                "risk": option.risk,
                "dependency": list(option.dependency),
                "affected_area": list(option.affected_area),
                "adr_candidates": list(option.adr_candidates),
                "wbs_candidates": list(option.wbs_candidates),
                "basis_references": list(option.basis_references),
            }
            for option in options
        ]
        (runtime_dir / "architecture_options.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
