from __future__ import annotations

from pathlib import Path
from typing import Any

from system.core.agent_execution_approval import evaluate_execution_approval, load_latest_handoff
from system.core.agent_role_registry import get_role
from system.core.business_agent_handoff import write_business_agent_handoff
from system.core.business_agent_task_queue import add_task, load_queue

# "Level 1" queue-population automation: proposing the next task is automatic,
# but nothing here ever writes an approval or runs anything. See
# docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md. Kept as a plain
# function, not a dispatcher/class -- this repo treats premature shared
# abstractions as a real risk (ADR-0032), and this only ever does two things:
# look up next_roles, call the two existing enqueue/activate primitives.


def evaluate_and_enqueue_next_tasks(
    business_id: str,
    role_id: str,
    task_id: str,
    artifact_path: str,
    base_path: str | Path = ".",
) -> list[dict[str, Any]]:
    role = get_role(role_id, base_path)
    if role is None or not role.next_roles:
        return []

    # Detect whether the current handoff slot is the task that JUST completed
    # (i.e. it's ours to overwrite) or some OTHER scope entirely. Checking
    # evaluate_execution_approval().allowed alone isn't enough here: right
    # after this task's own execution, its own approval still reads as
    # "allowed" (nothing invalidates it post-run), which would otherwise make
    # the very first next-task proposal after every success look "blocked."
    current_handoff = load_latest_handoff(base_path) or {}
    handoff_is_self = (
        current_handoff.get("business_id") == business_id
        and current_handoff.get("role_id") == role_id
        and current_handoff.get("task_id") == task_id
    )
    blocked_by_other_pending_approval = (not handoff_is_self) and evaluate_execution_approval(base_path).allowed

    enqueued: list[dict[str, Any]] = []
    for next_role_id in role.next_roles:
        auto_task_id = _next_auto_task_id(business_id, next_role_id, base_path)
        title = f"Auto-triggered {next_role_id} following {business_id}/{role_id}/{task_id}"
        task_description = (
            f"Auto-triggered following successful completion of {business_id}/{role_id}/{task_id}. "
            f"Read its artifact at {artifact_path} and produce the {next_role_id} output building on it."
        )
        add_task(business_id, next_role_id, auto_task_id, title, base_path, source="auto_trigger")

        # Anti-clobber guard: if a DIFFERENT scope's approval is currently
        # valid and pending execution, activating this new one would silently
        # overwrite it (single canonical agent_handoff/latest.json slot).
        # Enqueue only in that case -- the task stays visible in queue.json
        # and can be activated later by re-proposing it once the slot frees up.
        # Also caps activation to at most one per call: if next_roles ever
        # fans out to more than one role, only the first gets activated, the
        # rest enqueue-only, so this loop can't silently overwrite its own
        # just-activated sibling before a human ever sees it.
        activated = not blocked_by_other_pending_approval
        if activated:
            write_business_agent_handoff(business_id, next_role_id, auto_task_id, task_description, base_path)
            blocked_by_other_pending_approval = True

        enqueued.append(
            {
                "business_id": business_id,
                "role_id": next_role_id,
                "task_id": auto_task_id,
                "activated": activated,
            }
        )
    return enqueued


def _next_auto_task_id(business_id: str, role_id: str, base_path: str | Path) -> str:
    existing = [
        item
        for item in load_queue(base_path)
        if item.get("business_id") == business_id and item.get("role_id") == role_id
    ]
    return f"auto-{len(existing) + 1:04d}"
