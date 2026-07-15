from __future__ import annotations

import json
from pathlib import Path

from system.core.failure_store import append_failure, load_failures, update_retry_count


def test_failure_store_creates_file_and_appends_entry(tmp_path: Path) -> None:
    store = tmp_path / "system" / "runtime" / "knowledge" / "failures.json"

    assert load_failures(tmp_path) == []
    entry = append_failure(
        {
            "request_id": "REQ-1",
            "issue_number": 32,
            "error_type": "external_capacity",
            "model": "gpt-5.4-mini",
        },
        base_path=tmp_path,
    )

    assert store.exists()
    assert entry["retry_count"] == 1
    payload = json.loads(store.read_text(encoding="utf-8"))
    assert payload[-1]["request_id"] == "REQ-1"
    assert payload[-1]["issue_number"] == 32
    assert payload[-1]["error_type"] == "external_capacity"
    assert payload[-1]["model"] == "gpt-5.4-mini"
    assert payload[-1]["retry_count"] == 1


def test_failure_store_increments_retry_count_for_same_issue(tmp_path: Path) -> None:
    append_failure(
        {
            "request_id": "REQ-1",
            "issue_number": 32,
            "error_type": "unknown",
            "model": "gpt-5.4-mini",
        },
        base_path=tmp_path,
    )
    second = append_failure(
        {
            "request_id": "REQ-2",
            "issue_number": 32,
            "error_type": "usage_limit",
            "model": "gpt-5.4-mini",
        },
        base_path=tmp_path,
    )

    assert second["retry_count"] == 2
    failures = load_failures(tmp_path)
    assert len(failures) == 2
    assert update_retry_count(32, failures) == 3


def test_failure_store_resets_retry_count_for_new_issue(tmp_path: Path) -> None:
    append_failure(
        {
            "request_id": "REQ-1",
            "issue_number": 32,
            "error_type": "unknown",
            "model": "gpt-5.4-mini",
        },
        base_path=tmp_path,
    )
    entry = append_failure(
        {
            "request_id": "REQ-2",
            "issue_number": 33,
            "error_type": "unknown",
            "model": "gpt-5.4-mini",
        },
        base_path=tmp_path,
    )

    assert entry["retry_count"] == 1
