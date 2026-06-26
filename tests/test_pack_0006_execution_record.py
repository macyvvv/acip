from __future__ import annotations

from pathlib import Path


def test_pack_0006_execution_record_exists() -> None:
    assert Path("docs/current/PACK_0006_EXECUTION_RECORD.md").exists()
