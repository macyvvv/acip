from __future__ import annotations

from orchestrator.github_actions_event_fixture import GitHubActionsEventFixtureReader


def test_github_actions_event_fixture_reader(tmp_path) -> None:
    fixture = tmp_path / "fixture.json"
    fixture.write_text('{"event_id":"evt-1","issue_id":14}', encoding="utf-8")
    result = GitHubActionsEventFixtureReader(tmp_path).read(fixture)
    assert result.event.event_id == "evt-1"
