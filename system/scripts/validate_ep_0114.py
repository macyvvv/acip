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
        ROOT / "system" / "orchestrator" / "capability_router.py",
        ROOT / "workers" / "capability_matcher.py",
        ROOT / "docs" / "current" / "CAPABILITY_ROUTING.md",
        ROOT / "docs" / "current" / "WORKER_ASSIGNMENT.md",
        ROOT / "docs" / "ep" / "README_EP0114_CAPABILITY_ROUTER.md",
        ROOT / "specs" / "EP-0114",
        ROOT / ".github" / "workflows" / "ep0114-capability-router.yml",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing capability router files:", ", ".join(missing))
        return 1
    print("EP-0114 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
