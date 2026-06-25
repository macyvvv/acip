from __future__ import annotations

from orchestrator.architecture_planner import ArchitectureOption
from orchestrator.specification_generator import SpecificationGenerator


def test_specification_generator_generates_specification() -> None:
    generator = SpecificationGenerator(".")
    option = ArchitectureOption(
        option_id="ARCH-REQ-0001",
        title="Architecture for build",
        tradeoff="tradeoff",
        risk="low",
        dependency=(),
        affected_area=(),
        adr_candidates=(),
        wbs_candidates=(),
        basis_references=(),
    )
    specification = generator.generate(option)
    assert specification.spec_id == "SPEC-arch-req-0001"
    assert "ARCH-REQ-0001" in specification.implementation_spec
    assert "python scripts/validate_all.py" in specification.validation
