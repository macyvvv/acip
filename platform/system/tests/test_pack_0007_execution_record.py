from __future__ import annotations

from pathlib import Path


def test_pack_0007_execution_record_exists() -> None:
    assert Path("platform/docs/current/PACK_0007_EXECUTION_RECORD.md").exists()
