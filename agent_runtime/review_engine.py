from __future__ import annotations

from .models import RuntimeContext, RuntimePlan, QueueItem, ReviewSummary


def build_review_summary(context: RuntimeContext, plan: RuntimePlan, queue_item: QueueItem) -> ReviewSummary:
    risks = [
        "Runtime execution remains unapproved.",
        "External action boundary must remain enforced.",
        "Secret use is prohibited.",
    ]
    evidence = [
        context.graph_path,
        context.context_pack_path,
        plan.plan_id,
        queue_item.task_id,
    ]
    return ReviewSummary(
        summary_id="ARMVP-REVIEW-0001",
        decision="approval_ready_for_dry_run_only",
        evidence=evidence,
        risks=risks,
        human_decision_required=True,
    )
