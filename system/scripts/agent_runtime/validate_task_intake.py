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
OUT = ROOT / "system" / "runtime" / "task_intake" / "ART-SAMPLE-0001"

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
