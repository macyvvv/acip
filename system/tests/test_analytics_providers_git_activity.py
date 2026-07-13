from __future__ import annotations

from system.scripts.analytics.providers import AnalyticsFetchError, get_provider
from system.scripts.analytics.providers_git_activity import GitActivityProvider


def test_git_activity_registered_via_optional_module() -> None:
    provider = get_provider("git_activity")
    assert isinstance(provider, GitActivityProvider)


def test_git_activity_reports_real_nonempty_metrics_for_active_business() -> None:
    result = GitActivityProvider().fetch("kabukicho_survival_map")
    assert result.provider == "git_activity"
    assert result.business_id == "kabukicho_survival_map"
    assert set(result.metrics) == {
        "commits_last_30d",
        "files_touched_last_30d",
        "days_since_last_commit",
    }
    assert "not real platform" in result.notes


def test_git_activity_greenfield_business_has_no_paths_to_measure() -> None:
    result = GitActivityProvider().fetch("music_platform")
    assert result.metrics == {}
    assert "nothing to measure" in result.notes


def test_git_activity_unknown_business_raises() -> None:
    try:
        GitActivityProvider().fetch("not_a_real_business")
        assert False, "expected AnalyticsFetchError"
    except AnalyticsFetchError:
        pass
