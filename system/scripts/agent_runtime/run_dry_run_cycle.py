#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_runtime.cycle import run_dry_run_cycle


if __name__ == "__main__":
    result = run_dry_run_cycle(ROOT)
    print("# Agent Runtime MVP Dry Run")
    print(f"status={result['status']}")
    print(f"output_dir={result['output_dir']}")
