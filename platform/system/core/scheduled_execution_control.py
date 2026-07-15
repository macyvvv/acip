from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Dedicated kill switch for Level 3b (system/scripts/business_agent/
# run_scheduled_execution.py) -- the 4th independent switch in this
# platform, deliberately not a reuse of any of the other three:
#
#   - is_automation_paused (business_agent_automation_control.py) only
#     promises to freeze Level 1/2 automatic next-task *proposal*; it says
#     nothing about whether an unattended process should keep *attempting*
#     already-queued work.
#   - is_pre_approval_paused (execution_pre_approval_control.py) already
#     independently gates the deeper policy-claim decision inside
#     ApprovedAutonomousExecution.run() -- reusing it here would conflate
#     "should this scope's policy currently authorize execution" with "should
#     the unattended scheduler loop even attempt anything this wake," which
#     are different operator concerns (you may want interactive/session-
#     triggered runs to keep working via pre-approval while freezing only the
#     background scheduler, e.g. while debugging a runaway loop).
#   - is_publishing_paused (publishing_control.py) governs the one
#     irreversible, externally-visible action (posting) and is intentionally
#     unrelated to generation-only work.
#
# Checked first, before the runner even looks at the candidate queue --
# paused means the scheduler does nothing at all this wake, full stop. No
# manual-override/force path, matching all three siblings.


def _sentinel_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system" / "runtime" / "scheduler" / "scheduler_paused.json"


def is_scheduled_execution_paused(base_path: str | Path = ".") -> bool:
    return _sentinel_path(base_path).exists()


def pause_scheduled_execution(reason: str, paused_by: str, base_path: str | Path = ".") -> Path:
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


def resume_scheduled_execution(base_path: str | Path = ".") -> bool:
    path = _sentinel_path(base_path)
    if not path.exists():
        return False
    path.unlink()
    return True


def scheduled_execution_pause_info(base_path: str | Path = ".") -> dict[str, Any] | None:
    path = _sentinel_path(base_path)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None
