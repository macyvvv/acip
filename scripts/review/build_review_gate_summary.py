#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "orchestrator" / "execution_plan.json"
OUT = ROOT / "review" / "REVIEW_GATE_SUMMARY.md"

def main() -> int:
    if not PLAN.exists():
        print("missing orchestrator/execution_plan.json")
        return 1
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    lines = [
        "# Review Gate Summary",
        "",
        "## Conclusion",
        "",
        "Repository OS v1.0 baseline review summary generated.",
        "",
        "## Execution Plan",
        "",
        f"- plan_id: {plan.get('plan_id')}",
        f"- task_id: {plan.get('task_id')}",
        f"- owner: {plan.get('owner')}",
        f"- validation: `{plan.get('validation')}`",
        "",
        "## Boundary",
        "",
        "- Runtime execution: not approved",
        "- External action: not performed",
        "- Human decision required: runtime transition only",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"review_summary={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
