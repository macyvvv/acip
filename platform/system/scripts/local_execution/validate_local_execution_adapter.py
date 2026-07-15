#!/usr/bin/env python3
from __future__ import annotations

import json
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
        ROOT / "contracts" / "LOCAL_EXECUTION_ADAPTER_CONTRACT.md",
        ROOT / "docs" / "current" / "LOCAL_EXECUTION_ADAPTER.md",
        ROOT / "runtime" / "local_execution" / "latest.json",
        ROOT / "runtime" / "local_execution" / "latest.md",
        ROOT / "orchestrator" / "local_execution_adapter.py",
        ROOT / "scripts" / "local_execution" / "run_claude_adapter.py",
        ROOT / "tests" / "test_local_execution_adapter.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing local execution adapter files:", ", ".join(missing))
        return 1
    payload = json.loads((ROOT / "runtime" / "local_execution" / "latest.json").read_text(encoding="utf-8"))
    if payload.get("adapter_mode") not in {"dry_run", "execute"}:
        print("FAIL: invalid adapter mode")
        return 1
    print("Local execution adapter validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
