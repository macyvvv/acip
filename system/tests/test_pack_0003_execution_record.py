from __future__ import annotations

from pathlib import Path


def test_pack_0003_execution_record_maps_child_eps() -> None:
    record = Path("docs/current/PACK_0003_EXECUTION_RECORD.md").read_text(encoding="utf-8")
    assert "PACK_0003_EXECUTION_RECORD" in record
    assert "Issue #4 / EP-0151 / commit `3b97372`" in record
    assert "Issue #8 / EP-0155 / commit `655ce87`" in record
