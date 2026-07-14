from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Dedicated kill switch for the unattended-merge capability added to
# system/scripts/business_agent/run_scheduled_execution.py (ADR-0040) --
# the 5th independent switch in this platform, deliberately not a reuse of
# any of the other four (see scheduled_execution_control.py's own docstring
# for the same reasoning applied to itself): "should a successful wake's
# opened PR be merged unattended" is a different operator concern from
# "should the wake attempt anything this cycle" (is_scheduled_execution_
# paused) -- an operator may want generation to keep running while pausing
# only the newer, higher-trust merge step, e.g. while investigating a
# suspect auto-merge.
#
# Also auto-engaged by the circuit breaker (see scheduled_merge_circuit.py)
# after repeated merge-gate failures -- paused_by="circuit_breaker" in that
# case, distinguishable from a human/operator pause.


def _sentinel_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system" / "runtime" / "scheduler" / "merge_paused.json"


def is_scheduled_merge_paused(base_path: str | Path = ".") -> bool:
    return _sentinel_path(base_path).exists()


def pause_scheduled_merge(reason: str, paused_by: str, base_path: str | Path = ".") -> Path:
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


def resume_scheduled_merge(base_path: str | Path = ".") -> bool:
    path = _sentinel_path(base_path)
    if not path.exists():
        return False
    path.unlink()
    return True


def scheduled_merge_pause_info(base_path: str | Path = ".") -> dict[str, Any] | None:
    path = _sentinel_path(base_path)
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None
