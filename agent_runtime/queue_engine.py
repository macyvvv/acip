from __future__ import annotations

from .models import RuntimePlan, QueueItem


def build_queue_item(plan: RuntimePlan) -> QueueItem:
    return QueueItem(
        task_id="ARMVP-TASK-0001",
        owner="Codex/scripts",
        objective=plan.objective,
        status="approval_ready",
        validation="python system/scripts/agent_runtime/validate_agent_runtime_mvp.py",
        done_condition="Dry-run cycle generates context, plan, queue, review, and approval-ready artifacts.",
    )
