#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "runtime" / "agent_runtime_mvp"

REQUIRED = [
    OUT / "runtime_context.json",
    OUT / "runtime_plan.json",
    OUT / "queue_item.json",
    OUT / "review_summary.json",
    OUT / "approval_gate.json",
    OUT / "DRY_RUN_REPORT.md",
]


def main() -> int:
    subprocess.check_call([sys.executable, "scripts/agent_runtime/run_dry_run_cycle.py"], cwd=ROOT)

    failures = []
    for path in REQUIRED:
        if not path.exists():
            failures.append(f"missing artifact: {path.relative_to(ROOT)}")

    if (OUT / "approval_gate.json").exists():
        gate = json.loads((OUT / "approval_gate.json").read_text(encoding="utf-8"))
        required = set(gate.get("requires_human_approval", []))
        for item in [
            "runtime external execution",
            "platform API mutation",
            "auto posting",
            "secret use",
            "runtime transition",
        ]:
            if item not in required:
                failures.append(f"approval gate missing: {item}")

    if failures:
        print("# Agent Runtime MVP Validation")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("# Agent Runtime MVP Validation")
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
