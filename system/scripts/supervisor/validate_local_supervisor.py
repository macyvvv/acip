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


def main() -> int:
    required = [
        ROOT / "contracts" / "LOCAL_AGENT_SUPERVISOR_CONTRACT.md",
        ROOT / "docs" / "current" / "LOCAL_AGENT_SUPERVISOR_BRIDGE.md",
        ROOT / "runtime" / "supervisor" / "latest.json",
        ROOT / "runtime" / "supervisor" / "latest.md",
        ROOT / "orchestrator" / "local_supervisor.py",
        ROOT / "scripts" / "supervisor" / "run_local_supervisor.py",
        ROOT / "tests" / "test_local_supervisor.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing local supervisor files:", ", ".join(missing))
        return 1
    print("Local supervisor validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
