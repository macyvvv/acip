#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
