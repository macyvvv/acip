#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from orchestrator.work_planner import WorkPlanner


def main() -> int:
    planner = WorkPlanner(ROOT)
    plan = planner.build()
    planner.write(plan)
    print("Work planner build completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
