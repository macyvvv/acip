from __future__ import annotations

from system.core.business_registry import build_business_registry


def test_seeds_four_businesses(tmp_path):
    registry = build_business_registry(tmp_path)
    assert registry["summary"]["business_count"] == 4
    business_ids = {item["business_id"] for item in registry["businesses"]}
    assert business_ids == {"kabukicho_survival_map", "somia", "music_platform", "text_syndicate"}


def test_active_businesses_flagged_drifted_when_paths_missing(tmp_path):
    registry = build_business_registry(tmp_path)
    assert set(registry["summary"]["drifted_business_ids"]) == {"kabukicho_survival_map", "somia"}


def test_active_businesses_not_drifted_when_paths_present(tmp_path):
    (tmp_path / "businesses" / "kabukicho_survival_map" / "app").mkdir(parents=True)
    (tmp_path / "businesses" / "somia" / "content").mkdir(parents=True)
    (tmp_path / "platform" / "system" / "scripts" / "somia").mkdir(parents=True)

    registry = build_business_registry(tmp_path)
    assert registry["summary"]["drifted_business_ids"] == []


def test_greenfield_businesses_never_drifted(tmp_path):
    registry = build_business_registry(tmp_path)
    music_platform = next(item for item in registry["businesses"] if item["business_id"] == "music_platform")
    text_syndicate = next(item for item in registry["businesses"] if item["business_id"] == "text_syndicate")
    assert music_platform["content_root"] is None
    assert music_platform["content_root_exists"] is False
    assert text_syndicate["historical_issue_numbers"] == ()
    assert music_platform["historical_issue_numbers"] == (32,)
