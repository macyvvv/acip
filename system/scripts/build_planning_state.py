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

from orchestrator.planning_state_builder import PlanningStateBuilder


def main() -> int:
    builder = PlanningStateBuilder(ROOT)
    state = builder.build()
    builder.write(state)
    print("Planning state projection built.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
