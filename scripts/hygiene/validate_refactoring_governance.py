from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def validate_refactoring_governance(path: str | Path = ROOT / "docs" / "current" / "REFACTORING_GOVERNANCE_GATE.md") -> None:
    text = Path(path).read_text(encoding="utf-8")
    required_fragments = [
        "high risk requires Human approval",
        "rollback plan is mandatory",
        "validation requirement is mandatory",
        "changed path allowlist is mandatory",
        "destructive change is prohibited unless explicitly approved",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    if missing:
        raise ValueError(f"Missing governance fields: {', '.join(missing)}")
