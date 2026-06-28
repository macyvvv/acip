from __future__ import annotations

from system.orchestrator.repository_governor import RepositoryGovernor


def test_repository_governor_loads_persisted_recommendation() -> None:
    governor = RepositoryGovernor(".")
    recommendation = governor.load_recommendation()
    assert recommendation.version == 1
