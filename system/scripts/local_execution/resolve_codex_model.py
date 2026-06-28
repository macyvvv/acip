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

from system.orchestrator.local_execution_adapter import LocalExecutionAdapter


def main() -> int:
    adapter = LocalExecutionAdapter(ROOT)
    request = adapter._read_request() or {"request_id": "REQ-UNKNOWN", "request_status": "ready", "next_action": "unknown"}
    planning = adapter._read_json(ROOT / "runtime" / "planning" / "latest.json")
    repository = adapter._read_json(ROOT / "runtime" / "repository_state" / "latest.json")
    resolution = adapter._resolve_model(request, planning, repository)
    print(resolution["resolved_model"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
