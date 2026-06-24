#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "orchestrator" / "context_bundle.json"
OUT = ROOT / "orchestrator" / "execution_plan.json"

def main() -> int:
    if not BUNDLE.exists():
        subprocess.check_call([sys.executable, "scripts/orchestrator/build_context_bundle.py"], cwd=ROOT)

    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))

    plan = {
        "plan_id": "OEP-0001",
        "task_id": bundle["task_id"],
        "owner": "Codex/scripts",
        "objective": "Validate Agent Orchestrator preparation without runtime execution",
        "context_bundle": "orchestrator/context_bundle.json",
        "steps": [
            "Read context bundle",
            "Verify repository graph exists",
            "Verify agent context pack exists",
            "Validate Human Boundary",
            "Validate Runtime Boundary",
            "Run orchestrator validation",
        ],
        "validation": "python scripts/orchestrator/validate_orchestration.py",
        "done_condition": "Validation passes and no runtime execution occurs",
        "escalation_condition": "Human approval required only for runtime transition, risk acceptance, capital allocation, or emergency stop",
        "prohibited_actions": bundle["prohibited_actions"],
    }

    OUT.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"execution_plan={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
