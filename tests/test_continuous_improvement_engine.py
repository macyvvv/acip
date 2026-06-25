from __future__ import annotations

from orchestrator.continuous_improvement_engine import ContinuousImprovementEngine


def test_continuous_improvement_engine_builds_ranked_plan() -> None:
    engine = ContinuousImprovementEngine(".")
    plan = engine.build_plan()
    assert plan.candidates
    values = [candidate.value for candidate in plan.candidates]
    assert values == sorted(values, reverse=True)
