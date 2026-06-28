#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
PLAN = ROOT / "orchestrator" / "execution_plan.json"
OUT = ROOT / "orchestrator" / "EXECUTION_QUEUE.md"

def main() -> int:
    if not PLAN.exists():
        subprocess.check_call([sys.executable, "scripts/orchestrator/build_execution_plan.py"], cwd=ROOT)

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    content = f"""# Execution Queue

| task_id | objective | owner | validation | status | done_condition |
|---|---|---|---|---|---|
| {plan.get('task_id')} | {plan.get('objective')} | {plan.get('owner')} | {plan.get('validation')} | ready | {plan.get('done_condition')} |

## Boundary

Runtime execution remains prohibited until explicit Human approval.
"""
    OUT.write_text(content, encoding="utf-8")
    print(f"execution_queue={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
