from __future__ import annotations

from orchestrator.repository_governor import RepositoryGovernor


def test_repository_governor_generates_deterministic_candidates() -> None:
    governor = RepositoryGovernor(".")
    candidates = governor.build_candidates()
    assert candidates == tuple(sorted(candidates, key=lambda item: (-item.priority, item.ep)))


def test_repository_governor_recommendation_has_state() -> None:
    governor = RepositoryGovernor(".")
    recommendation = governor.recommend()
    assert recommendation.state.next_ep
    assert recommendation.candidates
