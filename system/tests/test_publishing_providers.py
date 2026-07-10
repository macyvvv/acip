from __future__ import annotations

import pytest

from system.scripts.publishing.providers import DryRunProvider, PublishError, get_provider


def test_dry_run_provider_shape() -> None:
    provider = DryRunProvider()
    result = provider.publish("x", "hello world", "text_syndicate")
    assert result.provider == "dry_run"
    assert result.platform == "x"
    assert result.business_id == "text_syndicate"
    assert result.external_post_id is None
    assert "dry-run" in result.notes


def test_default_provider_is_dry_run() -> None:
    provider = get_provider()
    assert provider.name == "dry_run"


def test_unresolvable_provider_raises_with_known_list() -> None:
    with pytest.raises(PublishError) as exc_info:
        get_provider("x")
    assert "x" in str(exc_info.value)
    assert "dry_run" in str(exc_info.value)
