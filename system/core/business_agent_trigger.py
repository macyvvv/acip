from __future__ import annotations

from pathlib import Path
from typing import Any

from system.core.agent_role_registry import get_role
from system.core.business_agent_handoff import write_business_agent_handoff
from system.core.business_agent_task_queue import add_task, load_queue

# Level 1 (queue population) + Level 2 (per-task scoping) automation: proposing
# and activating the next task is automatic, but nothing here ever writes an
# approval or runs anything. See docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md.
# Kept as a plain function, not a dispatcher/class -- this repo treats
# premature shared abstractions as a real risk (ADR-0032), and this only ever
# does two things: look up next_roles, call the two enqueue/activate primitives.
#
# No anti-clobber guard: each (business, role, task) scope has its own
# handoff/approval files (system/core/business_agent_handoff.py's
# per-task scope_dir), so two different scopes never share a slot and there
# is nothing left to clobber. This is what Level 2 removed, not narrowed --
# see adr/ADR-0034.


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

    enqueued: list[dict[str, Any]] = []
    for next_role_id in role.next_roles:
        auto_task_id = _next_auto_task_id(business_id, next_role_id, base_path)
        title = f"Auto-triggered {next_role_id} following {business_id}/{role_id}/{task_id}"
        task_description = (
            f"Auto-triggered following successful completion of {business_id}/{role_id}/{task_id}. "
            f"Read its artifact at {artifact_path} and produce the {next_role_id} output building on it."
        )
        add_task(business_id, next_role_id, auto_task_id, title, base_path, source="auto_trigger")
        write_business_agent_handoff(business_id, next_role_id, auto_task_id, task_description, base_path)

        enqueued.append(
            {
                "business_id": business_id,
                "role_id": next_role_id,
                "task_id": auto_task_id,
                "activated": True,
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
