#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
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
    failures = []
    for path in REQUIRED:
        if not path.exists():
            failures.append(f"missing artifact: {path.relative_to(ROOT)}")

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
