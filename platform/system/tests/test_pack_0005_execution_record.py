from __future__ import annotations

from pathlib import Path


def test_pack_0005_execution_record_exists() -> None:
    record = Path("docs/current/PACK_0005_EXECUTION_RECORD.md").read_text(encoding="utf-8")
    assert "PACK_0005_EXECUTION_RECORD" in record
    assert "Issue #14 / EP-0161" in record
    assert "Issue #19 / EP-0166" in record
