from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Kill switch for the Level 3c publishing scheduler (system/scripts/publishing/
# run_scheduled_publish.py). Kept separate from system/core/business_agent_
# automation_control.py's task-proposal switch on purpose: "stop new tasks
# from being queued" and "stop already-approved content from posting
# externally" are different operator concerns, and an operator investigating
# one shouldn't be forced to also freeze the other. The scheduler itself
# checks BOTH switches (is_publishing_paused() here AND is_automation_paused()
# from the sibling module) and treats either as a full stop -- so an operator
# reaching for the more familiar pause_automation.py during an incident still
# gets the safety they'd reasonably expect. Unlike the sibling switch, there
# is no manual-override/force path: publishing is the one irreversible,
# externally-visible action in this platform, so paused means zero posts,
# full stop, until an explicit resume_publishing() call.


def _sentinel_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system" / "runtime" / "publishing" / "publishing_paused.json"


def is_publishing_paused(base_path: str | Path = ".") -> bool:
    return _sentinel_path(base_path).exists()


def pause_publishing(reason: str, paused_by: str, base_path: str | Path = ".") -> Path:
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


def resume_publishing(base_path: str | Path = ".") -> bool:
    path = _sentinel_path(base_path)
    if not path.exists():
        return False
    path.unlink()
    return True


def publishing_pause_info(base_path: str | Path = ".") -> dict[str, Any] | None:
    path = _sentinel_path(base_path)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None
