from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_root_hygiene_migration_plan_exists() -> None:
    assert (ROOT / "docs" / "current" / "ROOT_HYGIENE_MIGRATION_PLAN.md").exists()


def test_root_has_no_ep_migration_candidates() -> None:
    candidates = []
    for pattern in ("README_EP*.md", "MANIFEST_EP*.md", "*_PACK.md"):
        candidates.extend(ROOT.glob(pattern))
    assert candidates == []
