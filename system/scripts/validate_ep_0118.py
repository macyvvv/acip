#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "docs" / "current" / "ROOT_HYGIENE_MIGRATION_PLAN.md",
        ROOT / "docs" / "ep" / "README_EP0118_ROOT_HYGIENE_MIGRATION_1.md",
        ROOT / "specs" / "EP-0118",
        ROOT / "system" / "scripts" / "validate_ep_0118.py",
        ROOT / "system" / "tests" / "test_root_hygiene_migration.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0118 files:", ", ".join(missing))
        return 1

    root_candidates = [
        path
        for pattern in ("README_EP*.md", "MANIFEST_EP*.md", "*_PACK.md")
        for path in ROOT.glob(pattern)
    ]
    if root_candidates:
        print("FAIL: root migration candidates remain:", ", ".join(sorted(path.name for path in root_candidates)))
        return 1

    print("EP-0118 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
