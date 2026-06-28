from __future__ import annotations

from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
def test_root_hygiene_migration_plan_exists() -> None:
    assert (ROOT / "docs" / "current" / "ROOT_HYGIENE_MIGRATION_PLAN.md").exists()


def test_root_has_no_ep_migration_candidates() -> None:
    candidates = []
    for pattern in ("README_EP*.md", "MANIFEST_EP*.md", "*_PACK.md"):
        candidates.extend(ROOT.glob(pattern))
    assert candidates == []
