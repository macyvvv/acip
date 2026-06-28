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
        ROOT / "packs" / "PACK-0001-solution-development" / "pack.yaml",
        ROOT / "packs" / "PACK-0001-solution-development" / "README.md",
        ROOT / "docs" / "current" / "SOLUTION_DEVELOPMENT_PACK.md",
        ROOT / "specs" / "EP-0136",
        ROOT / "system" / "scripts" / "validate_ep_0136.py",
        ROOT / "system" / "tests" / "test_solution_development_pack.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0136 files:", ", ".join(missing))
        return 1
    print("EP-0136 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
