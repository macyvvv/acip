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

    assert schema["properties"]["store_type"]["enum"] == ["concept_cafe", "girls_bar"]


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


def _minimal_valid_record() -> dict:
    return {
        "schema_version": "store-artifact:v1",
        "store_id": "example-store-001",
        "store_name": "Example Store",
        "store_type": "concept_cafe",
        "status": "open",
        "address": "Tokyo, Shinjuku-ku, Example 1-2-3",
        "area": "歌舞伎町",
        "hours": [{"day_of_week": "mon", "open": "18:00", "close": "24:00"}],
        "pricing_model": "time_based_seat_charge",
        "price_items": [{"label": "30-min seat charge", "amount_jpy": 1500, "unit": "per_30min"}],
        "source_url": ["https://example.invalid/store"],
        "retrieved_at": "2026-07-21T00:00:00Z",
        "last_confirmed_at": "2026-07-21T00:00:00Z",
        "verification_method": "official-site",
        "reliability_score": 3,
        "change_log": [
            {
                "changed_at": "2026-07-21T00:00:00Z",
                "field": "status",
                "change_type": "initial_capture",
                "source_url": "https://example.invalid/store",
            }
        ],
    }


def test_minimal_valid_record_has_every_required_field() -> None:
    schema = _load_schema()
    record = _minimal_valid_record()

    missing = [field for field in schema["required"] if field not in record]
    assert missing == []
    assert set(record) <= set(schema["properties"])


def test_empty_price_items_requires_reason_field() -> None:
    schema = _load_schema()
    record = _minimal_valid_record()
    record["price_items"] = []

    conditional = schema["allOf"][0]
    assert conditional["then"]["required"] == ["price_unavailable_reason"]
    assert "price_unavailable_reason" not in record
