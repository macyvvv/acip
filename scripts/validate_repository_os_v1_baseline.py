#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "scripts/baseline/validate_baseline.py"],
    [sys.executable, "scripts/graph/build_repository_graph.py"],
    [sys.executable, "scripts/context/build_agent_context_pack.py"],
    [sys.executable, "scripts/orchestrator/build_context_bundle.py"],
    [sys.executable, "scripts/orchestrator/build_execution_plan.py"],
    [sys.executable, "scripts/graph/build_incremental_graph.py"],
    [sys.executable, "scripts/context/build_context_diff.py"],
    [sys.executable, "scripts/orchestrator/update_execution_queue.py"],
    [sys.executable, "scripts/review/build_review_gate_summary.py"],
]

def main() -> int:
    for cmd in COMMANDS:
        print("$ " + " ".join(cmd))
        subprocess.check_call(cmd, cwd=ROOT)
    print("Repository OS v1.0 baseline validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
