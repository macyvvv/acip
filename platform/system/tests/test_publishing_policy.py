from __future__ import annotations

import json
from pathlib import Path

import pytest

from system.core.publishing_policy import (
    PublishingPolicyError,
    get_publishing_policy,
    load_publishing_policies,
)


def _write_policy(tmp_path: Path, policies: list[dict]) -> None:
    path = tmp_path / "platform/system/runtime/publishing/policy.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "policies": policies}))


def _entry(**overrides) -> dict:
    base = {
        "policy_id": "PUBPOLICY-TEXT_SYNDICATE-X-0001",
        "business_id": "text_syndicate",
        "platform": "x",
        "enabled": True,
        "provider": "dry_run",
        "allowed_source_roles": ["marketing", "doc_creation"],
        "max_posts_per_day": 3,
        "max_posts_per_week": 10,
        "require_disclosure_tag_for_affiliate_content": True,
        "authored_by": "macy",
        "authored_at": "2026-07-10T00:00:00+00:00",
        "reason": "pilot",
    }
    base.update(overrides)
    return base


def test_missing_file_returns_none(tmp_path: Path) -> None:
    assert get_publishing_policy("text_syndicate", "x", tmp_path) is None
    assert load_publishing_policies(tmp_path) == []


def test_well_formed_load_and_lookup(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry()])
    record = get_publishing_policy("text_syndicate", "x", tmp_path)
    assert record is not None
    assert record.business_id == "text_syndicate"
    assert record.platform == "x"
    assert record.allowed_source_roles == ("marketing", "doc_creation")
    assert record.max_posts_per_day == 3


def test_missing_entry_returns_none(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry()])
    assert get_publishing_policy("text_syndicate", "threads", tmp_path) is None
    assert get_publishing_policy("kabukicho_survival_map", "x", tmp_path) is None


def test_disabled_entry_returns_none(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(enabled=False)])
    assert get_publishing_policy("text_syndicate", "x", tmp_path) is None


def test_unknown_platform_raises(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(platform="instagram")])
    with pytest.raises(PublishingPolicyError):
        load_publishing_policies(tmp_path)


def test_disallowed_source_role_raises(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(allowed_source_roles=["market_research"])])
    with pytest.raises(PublishingPolicyError):
        load_publishing_policies(tmp_path)


def test_non_positive_cap_raises(tmp_path: Path) -> None:
    _write_policy(tmp_path, [_entry(max_posts_per_day=0)])
    with pytest.raises(PublishingPolicyError):
        load_publishing_policies(tmp_path)


def test_cross_scope_isolation(tmp_path: Path) -> None:
    _write_policy(
        tmp_path,
        [
            _entry(policy_id="A", business_id="text_syndicate", platform="x"),
            _entry(policy_id="B", business_id="kabukicho_survival_map", platform="threads", max_posts_per_day=1),
        ],
    )
    a = get_publishing_policy("text_syndicate", "x", tmp_path)
    b = get_publishing_policy("kabukicho_survival_map", "threads", tmp_path)
    assert a.max_posts_per_day == 3
    assert b.max_posts_per_day == 1
    assert get_publishing_policy("text_syndicate", "threads", tmp_path) is None
