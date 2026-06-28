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
def main() -> int:
    required = [
        ROOT / "contracts" / "PLANNING_STATE_CONTRACT.md",
        ROOT / "docs" / "current" / "PLANNING_OS.md",
        ROOT / "runtime" / "planning" / "latest.json",
        ROOT / "runtime" / "planning" / "latest.md",
        ROOT / "orchestrator" / "planning_state_builder.py",
        ROOT / "tests" / "test_planning_state_builder.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing planning state files:", ", ".join(missing))
        return 1
    payload = json.loads((ROOT / "runtime" / "planning" / "latest.json").read_text(encoding="utf-8"))
    for key in ["mission", "long_term_goal", "current_phase", "current_objective", "current_scope", "current_pack", "current_ep", "wbs", "approved_next_action", "parking_lot", "refactoring_priorities", "blocked_items", "approval_required", "source_artifacts"]:
        if key not in payload:
            print(f"FAIL: missing field {key}")
            return 1
    print("Planning state validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
