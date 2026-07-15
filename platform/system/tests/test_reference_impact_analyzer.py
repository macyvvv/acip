from __future__ import annotations

from system.orchestrator.reference_impact_analyzer import ReferenceImpactAnalyzer


def test_reference_impact_analyzer_writes_report(tmp_path) -> None:
    impacts = ReferenceImpactAnalyzer(tmp_path).analyze()
    assert impacts
