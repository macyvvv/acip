#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
COMMANDS = [
    [sys.executable, "system/scripts/baseline/validate_baseline.py"],
    [sys.executable, "system/scripts/graph/build_repository_graph.py"],
    [sys.executable, "system/scripts/context/build_agent_context_pack.py"],
    [sys.executable, "system/scripts/orchestrator/build_context_bundle.py"],
    [sys.executable, "system/scripts/orchestrator/build_execution_plan.py"],
    [sys.executable, "system/scripts/graph/build_incremental_graph.py"],
    [sys.executable, "system/scripts/context/build_context_diff.py"],
    [sys.executable, "system/scripts/orchestrator/update_execution_queue.py"],
    [sys.executable, "system/scripts/review/build_review_gate_summary.py"],
]

def main() -> int:
    for cmd in COMMANDS:
        print("$ " + " ".join(cmd))
        subprocess.check_call(cmd, cwd=ROOT)
    print("Repository OS v1.0 baseline validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
