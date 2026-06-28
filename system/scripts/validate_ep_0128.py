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
        ROOT / "orchestrator" / "execution_kernel.py",
        ROOT / "orchestrator" / "autonomous_planning_cycle.py",
        ROOT / "docs" / "current" / "EXECUTION_KERNEL.md",
        ROOT / "docs" / "current" / "AUTONOMOUS_PLANNING_CYCLE.md",
        ROOT / "runtime" / "planning" / "autonomous_plan.json",
        ROOT / "specs" / "EP-0128",
        ROOT / "scripts" / "validate_ep_0128.py",
        ROOT / "tests" / "test_execution_kernel_planning_cycle.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0128 files:", ", ".join(missing))
        return 1
    print("EP-0128 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
