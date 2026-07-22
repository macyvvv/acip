from __future__ import annotations

import json
from pathlib import Path

BUSINESS_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = BUSINESS_ROOT / "schemas" / "source-register.json"
REGISTER_PATH = BUSINESS_ROOT / "artifacts" / "S-011" / "source-register.json"

DENIED_COMPETITOR_SOURCE_IDS = {"pokepara-jp", "moesta-com", "con-cafe-jp", "caferun-jp"}


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _load_entries() -> list[dict]:
    return json.loads(REGISTER_PATH.read_text(encoding="utf-8"))["entries"]


def test_schema_file_is_valid_json_schema_shape() -> None:
    schema = _load_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) <= set(schema["properties"])


def test_register_is_marked_draft_pending_human_signoff() -> None:
    payload = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))

    assert "DRAFT" in payload["note"]
    assert "Human" in payload["note"]


def test_every_entry_has_all_required_fields() -> None:
    schema = _load_schema()
    entries = _load_entries()

    for entry in entries:
        missing = [field for field in schema["required"] if field not in entry]
        assert missing == [], f"{entry.get('source_id')} missing {missing}"
        assert entry["decision"] in {"allow", "conditional", "deny"}


def test_named_competitor_aggregators_are_denied() -> None:
    entries = {entry["source_id"]: entry for entry in _load_entries()}

    assert DENIED_COMPETITOR_SOURCE_IDS <= set(entries)
    for source_id in DENIED_COMPETITOR_SOURCE_IDS:
        assert entries[source_id]["decision"] == "deny"


def test_no_entry_permits_pii_collection_in_this_phase() -> None:
    entries = _load_entries()

    assert all(entry["classification"] != "contains_pii" for entry in entries)


def test_conditional_entries_declare_at_least_one_condition() -> None:
    entries = _load_entries()

    for entry in entries:
        if entry["decision"] == "conditional":
            assert len(entry["conditions"]) >= 1, entry["source_id"]
