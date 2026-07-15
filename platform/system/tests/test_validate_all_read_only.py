from __future__ import annotations

from pathlib import Path


def test_validate_all_does_not_write_reports_by_default() -> None:
    text = Path("system/scripts/validate_all.py").read_text(encoding="utf-8")
    assert "write_reports" not in text
