#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_runtime.cycle import run_dry_run_cycle


if __name__ == "__main__":
    result = run_dry_run_cycle(ROOT)
    print("# Agent Runtime MVP Dry Run")
    print(f"status={result['status']}")
    print(f"output_dir={result['output_dir']}")
