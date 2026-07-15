from __future__ import annotations

from pathlib import Path

from .repository import find_repository_root
from .loader import load_runtime_context
from .planner import build_plan
from .queue_engine import build_queue_item
from .review_engine import build_review_summary
from .approval_gate import build_approval_gate
from .task_intake import load_task, write_task
from .models import write_json


def run_task_intake_cycle(task_path: Path, start: Path | None = None) -> dict:
    root = find_repository_root(start)
    task = load_task(root / task_path if not task_path.is_absolute() else task_path)
    context = load_runtime_context(root)
    base_plan = build_plan(context)

    plan_payload = base_plan.to_dict()
    plan_payload["plan_id"] = f"{base_plan.plan_id}-{task.task_id}"
    plan_payload["objective"] = task.objective
    plan_payload["task"] = task.to_dict()

    queue_item = build_queue_item(base_plan)
    queue_payload = queue_item.to_dict()
    queue_payload["task_id"] = task.task_id
    queue_payload["objective"] = task.objective
    queue_payload["status"] = "approval_ready"

    review = build_review_summary(context, base_plan, queue_item)
    review_payload = review.to_dict()
    review_payload["source_task"] = task.task_id
    review_payload["decision"] = "approval_ready_for_task_dry_run_only"

    approval_gate = build_approval_gate(review)
    approval_gate["source_task"] = task.task_id

    out_dir = root / "system" / "runtime" / "task_intake" / task.task_id
    write_task(out_dir / "normalized_task.json", task)
    write_json(out_dir / "runtime_context.json", context.to_dict())
    write_json(out_dir / "runtime_plan.json", plan_payload)
    write_json(out_dir / "queue_item.json", queue_payload)
    write_json(out_dir / "review_summary.json", review_payload)
    write_json(out_dir / "approval_gate.json", approval_gate)

    report = [
        "# Agent Runtime Task Intake Dry Run Report",
        "",
        "## Conclusion",
        "",
        "Task intake dry-run cycle completed without runtime external execution.",
        "",
        "## Task",
        "",
        f"- task_id: `{task.task_id}`",
        f"- title: {task.title}",
        f"- objective: {task.objective}",
        f"- priority: {task.priority}",
        "",
        "## Boundary",
        "",
        "- Runtime external execution: not performed",
        "- Platform API mutation: not performed",
        "- Auto posting: not performed",
        "- Secret use: not performed",
        "- Human approval: required for runtime transition or external execution",
    ]
    (out_dir / "TASK_INTAKE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    return {
        "status": "passed",
        "task_id": task.task_id,
        "output_dir": str(out_dir.relative_to(root)),
    }
