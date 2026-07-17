from __future__ import annotations

from .models import RuntimeContext, RuntimePlan


def build_plan(context: RuntimeContext) -> RuntimePlan:
    return RuntimePlan(
        plan_id="ARMVP-PLAN-0001",
        objective="Run a dry-run agent cycle from Repository SSOT",
        steps=[
            "Load repository graph",
            "Load agent context pack",
            "Build dry-run plan",
            "Create execution queue item",
            "Build review summary",
            "Produce approval-ready report",
        ],
        validation=[
            "python platform/system/scripts/agent_runtime/run_dry_run_cycle.py",
            "python platform/system/scripts/agent_runtime/validate_agent_runtime_mvp.py",
        ],
        prohibited_actions=[
            "runtime external execution",
            "platform API mutation",
            "auto posting",
            "scraping-dependent automation",
            "secret use",
            "approval bypass",
        ],
        approval_required=True,
    )
