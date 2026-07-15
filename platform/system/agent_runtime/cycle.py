from __future__ import annotations

from pathlib import Path

from .repository import find_repository_root
from .loader import load_runtime_context
from .planner import build_plan
from .queue_engine import build_queue_item
from .review_engine import build_review_summary
from .approval_gate import build_approval_gate
from .models import write_json


def run_dry_run_cycle(start: Path | None = None) -> dict:
    root = find_repository_root(start)
    context = load_runtime_context(root)
    plan = build_plan(context)
    queue_item = build_queue_item(plan)
    review = build_review_summary(context, plan, queue_item)
    approval_gate = build_approval_gate(review)

    out_dir = root / "system" / "runtime" / "agent_runtime_mvp"
    write_json(out_dir / "runtime_context.json", context.to_dict())
    write_json(out_dir / "runtime_plan.json", plan.to_dict())
    write_json(out_dir / "queue_item.json", queue_item.to_dict())
    write_json(out_dir / "review_summary.json", review.to_dict())
    write_json(out_dir / "approval_gate.json", approval_gate)

    report = [
        "# Agent Runtime MVP Dry Run Report",
        "",
        "## Conclusion",
        "",
        "Dry-run agent cycle completed without runtime external execution.",
        "",
        "## Generated Artifacts",
        "",
        "- `platform/system/runtime/agent_runtime_mvp/runtime_context.json`",
        "- `platform/system/runtime/agent_runtime_mvp/runtime_plan.json`",
        "- `platform/system/runtime/agent_runtime_mvp/queue_item.json`",
        "- `platform/system/runtime/agent_runtime_mvp/review_summary.json`",
        "- `platform/system/runtime/agent_runtime_mvp/approval_gate.json`",
        "",
        "## Boundary",
        "",
        "- Runtime external execution: not performed",
        "- Platform API mutation: not performed",
        "- Auto posting: not performed",
        "- Secret use: not performed",
        "- Human approval: required for runtime transition",
    ]
    (out_dir / "DRY_RUN_REPORT.md").write_text("\\n".join(report) + "\\n", encoding="utf-8")

    return {
        "status": "passed",
        "output_dir": str(out_dir.relative_to(root)),
        "artifacts": [
            "runtime_context.json",
            "runtime_plan.json",
            "queue_item.json",
            "review_summary.json",
            "approval_gate.json",
            "DRY_RUN_REPORT.md",
        ],
    }
