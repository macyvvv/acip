from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_request_id(business_id: str, role_id: str, task_id: str) -> str:
    """Deterministic handoff/approval ID for a (business, role, task) tuple.
    Public so the Approval Console can compute a scope-specific handoff_id
    for a queued-but-not-yet-active candidate, instead of echoing whatever
    happens to be the currently active handoff's request_id."""
    safe = f"{business_id}-{role_id}-{task_id}".replace("_", "-").replace(":", "-").replace("/", "-")
    return f"REQ-{safe.upper()}"


def write_business_agent_handoff(
    business_id: str,
    role_id: str,
    task_id: str,
    task_description: str,
    base_path: str | Path = ".",
) -> Path:
    """Writes directly to the same canonical single-slot handoff file the
    issue/draft flow uses (system/runtime/agent_handoff/latest.json) -- this
    repo's model is one active scope at a time, and this keeps that true for
    business-agent scopes too. Deliberately does not go through
    AgentIssueBridge / agent_thread_runner (placeholder machinery, no real
    work happens there -- see project memory acip-repo-audit-2026-07)."""
    root = Path(base_path)
    handoff_dir = root / "system" / "runtime" / "agent_handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    request_id = compute_request_id(business_id, role_id, task_id)
    payload: dict[str, Any] = {
        "business_id": business_id,
        "role_id": role_id,
        "task_id": task_id,
        "task_description": task_description,
        "issue_number": None,
        "approved_draft_id": None,
        "request_id": request_id,
        "next_action": "Review the handoff and, if approved, continue through the existing execution flow.",
        "created_at": _now(),
        "source": "business_agent_handoff",
    }
    handoff_path = handoff_dir / "latest.json"
    handoff_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (handoff_dir / "latest.md").write_text(_to_markdown(payload), encoding="utf-8")
    return handoff_path


def _to_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# AGENT_HANDOFF",
            "",
            f"business_id: {payload.get('business_id', '')}",
            f"role_id: {payload.get('role_id', '')}",
            f"task_id: {payload.get('task_id', '')}",
            f"task_description: {payload.get('task_description', '')}",
            f"request_id: {payload.get('request_id', '')}",
            f"next_action: {payload.get('next_action', '')}",
            "",
        ]
    )
