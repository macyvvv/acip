#!/usr/bin/env python3
from __future__ import annotations

import os
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

from system.orchestrator.local_execution_adapter import LocalExecutionAdapter


def main() -> int:
    approval_flag = os.environ.get("APPROVAL_FLAG", "false").lower() == "true"
    adapter = LocalExecutionAdapter(ROOT)
    adapter.run(approval_flag=approval_flag, dry_run=not approval_flag)
    print("Local execution adapter completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
