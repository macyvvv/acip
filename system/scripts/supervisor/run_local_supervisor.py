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

from system.orchestrator.local_supervisor import LocalSupervisor


def main() -> int:
    supervisor = LocalSupervisor(ROOT)
    supervisor.run(execution_flag=False)
    print("Local supervisor dry-run completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
