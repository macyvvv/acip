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
    [sys.executable, "scripts/graph/build_repository_graph.py"],
    [sys.executable, "scripts/graph/validate_repository_graph.py"],
    [sys.executable, "scripts/context/build_agent_context_pack.py"],
    [sys.executable, "scripts/runtime/dry_run_runtime_plan.py"],
]

def main() -> int:
    for cmd in COMMANDS:
        print("$ " + " ".join(cmd))
        subprocess.check_call(cmd, cwd=ROOT)
    print("Validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
