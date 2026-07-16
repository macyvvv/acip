from __future__ import annotations

from system.core.business_registry import build_business_registry, get_business


def test_seeds_five_businesses(tmp_path):
    registry = build_business_registry(tmp_path)
    assert registry["summary"]["business_count"] == 5
    business_ids = {item["business_id"] for item in registry["businesses"]}
    assert business_ids == {
        "cf_gb_relative_system",
        "kabukicho_survival_map",
        "music_platform",
        "somia",
        "text_syndicate",
    }


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


def test_cf_gb_relative_system_resolves_canonical_paths(tmp_path):
    app_root = tmp_path / "businesses" / "cf_gb_relative_system" / "app"
    app_root.mkdir(parents=True)

    business = get_business("cf_gb_relative_system", tmp_path)

    assert business is not None
    assert business.status == "greenfield"
    assert business.content_root == "businesses/cf_gb_relative_system/app"
    assert business.product_code_path == "businesses/cf_gb_relative_system/app"
    assert business.content_root_exists is True
    assert business.product_code_path_exists is True
