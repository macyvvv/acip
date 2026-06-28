#!/usr/bin/env python3
from __future__ import annotations

import json
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
    required = [
        ROOT / "contracts" / "WORK_PLANNER_CONTRACT.md",
        ROOT / "docs" / "current" / "WORK_PLANNER.md",
        ROOT / "runtime" / "work_planner" / "latest.json",
        ROOT / "runtime" / "work_planner" / "latest.md",
        ROOT / "orchestrator" / "work_planner.py",
        ROOT / "scripts" / "work_planner" / "build_work_plan.py",
        ROOT / "tests" / "test_work_planner.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing work planner files:", ", ".join(missing))
        return 1
    payload = json.loads((ROOT / "runtime" / "work_planner" / "latest.json").read_text(encoding="utf-8"))
    if not payload.get("candidate_items"):
        print("FAIL: missing candidate items")
        return 1
    print("Work planner validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
