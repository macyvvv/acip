#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime" / "task_intake" / "ART-SAMPLE-0001"

REQUIRED = [
    OUT / "normalized_task.json",
    OUT / "runtime_context.json",
    OUT / "runtime_plan.json",
    OUT / "queue_item.json",
    OUT / "review_summary.json",
    OUT / "approval_gate.json",
    OUT / "TASK_INTAKE_REPORT.md",
]


def main() -> int:
    subprocess.check_call([
        sys.executable,
        "scripts/agent_runtime/run_task_intake_cycle.py",
        "--task",
        "runtime/task_inputs/sample_task.json",
    ], cwd=ROOT)

    failures = []
    for path in REQUIRED:
        if not path.exists():
            failures.append(f"missing artifact: {path.relative_to(ROOT)}")

    if (OUT / "normalized_task.json").exists():
        task = json.loads((OUT / "normalized_task.json").read_text(encoding="utf-8"))
        if task.get("status") != "normalized":
            failures.append("normalized_task status must be normalized")
        if task.get("approval_required") is not True:
            failures.append("normalized_task approval_required must be true")

    if failures:
        print("# Agent Runtime Task Intake Validation")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("# Agent Runtime Task Intake Validation")
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
