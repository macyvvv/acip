from __future__ import annotations

from orchestrator.solution_development_runtime import SolutionDevelopmentRuntime


def test_solution_development_runtime_runs() -> None:
    runtime = SolutionDevelopmentRuntime(".")
    result = runtime.run("Build a repository-native solution development flow")
    assert result.pack_id == "PACK-0001"
    assert result.next_action == "ready"
