from __future__ import annotations

import json
from pathlib import Path

BUSINESS_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = BUSINESS_ROOT / "schemas" / "store-artifact.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_file_is_valid_json_schema_shape() -> None:
    schema = _load_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) <= set(schema["properties"])


def test_store_type_limited_to_current_business_scope() -> None:
    schema = _load_schema()

    assert schema["properties"]["store_type"]["enum"] == ["concept_cafe", "girls_bar", "unknown"]


def test_no_individual_cast_identifying_field_exists() -> None:
    schema = _load_schema()
    properties = schema["properties"]
    forbidden_terms = ("cast_name", "cast_photo", "cast_image", "cast_list", "cast_profile")

    assert "cast_headcount" in properties
    assert all(term not in properties for term in forbidden_terms)


def test_change_log_is_append_only_shaped_and_requires_source() -> None:
    schema = _load_schema()
    change_log_items = schema["properties"]["change_log"]["items"]

    assert "source_url" in change_log_items["required"]
    assert "changed_at" in change_log_items["required"]
    assert "previous_value" not in change_log_items["required"]


def _census_record(**overrides) -> dict:
    record = {
        "schema_version": "store-artifact:v1",
        "store_id": "example-store-001",
        "store_name": "Example Store",
        "store_type": "unknown",
        "status": "unknown",
        "area": "上野",
        "completeness_tier": "known",
        "source_url": ["web-search: varied queries, 2026-07-21"],
        "first_seen_at": "2026-07-21T00:00:00Z",
        "change_log": [],
    }
    record.update(overrides)
    return record


def _verified_record() -> dict:
    return _census_record(
        store_type="concept_cafe",
        status="open",
        completeness_tier="verified",
        address="Tokyo, Shinjuku-ku, Example 1-2-3",
        hours=[{"day_of_week": "mon", "open": "18:00", "close": "24:00"}],
        pricing_model="time_based_seat_charge",
        price_items=[{"label": "30-min seat charge", "amount_jpy": 1500, "unit": "per_30min"}],
        url="https://example.invalid/store",
        source_url=["https://example.invalid/store"],
        last_verified_at="2026-07-21T00:00:00Z",
        verification_method="official-site",
        reliability_score=3,
        change_log=[
            {
                "changed_at": "2026-07-21T00:00:00Z",
                "field": "status",
                "change_type": "initial_capture",
                "source_url": "https://example.invalid/store",
            }
        ],
    )


def test_bare_census_record_satisfies_top_level_required_fields() -> None:
    schema = _load_schema()
    record = _census_record()

    missing = [field for field in schema["required"] if field not in record]
    assert missing == []
    assert set(record) <= set(schema["properties"])


def test_census_record_does_not_need_enrichment_fields() -> None:
    # This is the whole point of the census pivot -- a name+existence-only
    # row must be a valid document without hours/pricing/verification_method.
    record = _census_record()

    for field in ("hours", "pricing_model", "price_items", "address", "verification_method", "reliability_score", "url"):
        assert field not in record


def test_has_official_source_tier_requires_a_url_or_sns_entry() -> None:
    schema = _load_schema()
    conditional = next(
        block for block in schema["allOf"]
        if block["if"]["properties"].get("completeness_tier", {}).get("enum") == ["has_official_source", "enriched", "verified"]
    )
    assert conditional["then"]["anyOf"][0]["required"] == ["url"]


def test_enriched_and_verified_tiers_require_structured_fields() -> None:
    schema = _load_schema()
    conditional = next(
        block for block in schema["allOf"]
        if block["if"]["properties"].get("completeness_tier", {}).get("enum") == ["enriched", "verified"]
    )
    assert set(conditional["then"]["required"]) == {"address", "hours", "pricing_model", "price_items"}


def test_verified_tier_requires_confirmation_fields() -> None:
    schema = _load_schema()
    conditional = next(
        block for block in schema["allOf"]
        if block["if"]["properties"].get("completeness_tier", {}).get("const") == "verified"
    )
    assert set(conditional["then"]["required"]) == {"verification_method", "reliability_score", "last_verified_at"}


def test_fully_verified_record_satisfies_every_conditional_requirement() -> None:
    schema = _load_schema()
    record = _verified_record()

    missing = [field for field in schema["required"] if field not in record]
    assert missing == []
    assert set(record) <= set(schema["properties"])


def test_empty_price_items_requires_reason_field() -> None:
    schema = _load_schema()
    record = _verified_record()
    record["price_items"] = []

    conditional = schema["allOf"][0]
    assert conditional["then"]["required"] == ["price_unavailable_reason"]
    assert "price_unavailable_reason" not in record
