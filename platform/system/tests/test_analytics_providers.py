from __future__ import annotations

from system.scripts.analytics.providers import AnalyticsFetchError, DryRunProvider, get_provider


def test_default_provider_is_dry_run() -> None:
    provider = get_provider()
    assert isinstance(provider, DryRunProvider)


def test_dry_run_provider_never_calls_network_and_returns_empty_metrics() -> None:
    result = DryRunProvider().fetch("text_syndicate")
    assert result.provider == "dry_run"
    assert result.business_id == "text_syndicate"
    assert result.metrics == {}


def test_unknown_provider_raises() -> None:
    try:
        get_provider("not_a_real_platform")
        assert False, "expected AnalyticsFetchError"
    except AnalyticsFetchError:
        pass
