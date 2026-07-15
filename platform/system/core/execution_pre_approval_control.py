from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Dedicated kill switch for Level 3a policy-based execution pre-approval
# (platform/system/core/execution_pre_approval_policy.py +
# platform/system/core/approved_autonomous_execution.py's _try_policy_pre_approval).
#
# Deliberately NOT the same switch as platform/system/core/business_agent_
# automation_control.py's is_automation_paused(). That switch's docstring
# is an explicit, load-bearing promise: pausing it "does not block a human
# from manually running... run_approved_autonomous_execution.py... an
# explicit human action stays explicit." If this module's check also
# consulted is_automation_paused(), the SAME CLI entry point / SAME
# function (ApprovedAutonomousExecution.run()) would behave differently
# for the same paused state depending on which authorization path a given
# scope happens to use -- quietly redefining that existing switch's
# contract for one of its two callers. is_automation_paused() is left
# completely untouched by this module and by everything in Level 3a.
#
# No manual-override/force path, matching both existing kill switches:
# paused means the pre-approval path denies every scope, full stop, until
# an explicit resume_pre_approval() call.


def _sentinel_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system" / "runtime" / "agent_handoff" / "auto_approval_paused.json"


def is_pre_approval_paused(base_path: str | Path = ".") -> bool:
    return _sentinel_path(base_path).exists()


def pause_pre_approval(reason: str, paused_by: str, base_path: str | Path = ".") -> Path:
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


def resume_pre_approval(base_path: str | Path = ".") -> bool:
    path = _sentinel_path(base_path)
    if not path.exists():
        return False
    path.unlink()
    return True


def pre_approval_pause_info(base_path: str | Path = ".") -> dict[str, Any] | None:
    path = _sentinel_path(base_path)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None
