from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Kill switch for Level 1/2 automatic next-task proposal (system/core/
# business_agent_trigger.py). Scoped narrowly and deliberately: pausing
# freezes auto-*proposal* only. It does not block a human from manually
# running propose_task.py, set_execution_approval.py, or
# run_approved_autonomous_execution.py -- an explicit human action stays
# explicit. See docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md.


def _sentinel_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system" / "runtime" / "business_agent_tasks" / "automation_paused.json"


def is_automation_paused(base_path: str | Path = ".") -> bool:
    return _sentinel_path(base_path).exists()


def pause_automation(reason: str, paused_by: str, base_path: str | Path = ".") -> Path:
    path = _sentinel_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "paused": True,
        "reason": reason,
        "paused_by": paused_by,
        "paused_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def resume_automation(base_path: str | Path = ".") -> bool:
    path = _sentinel_path(base_path)
    if not path.exists():
        return False
    path.unlink()
    return True


def automation_pause_info(base_path: str | Path = ".") -> dict[str, Any] | None:
    path = _sentinel_path(base_path)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None
