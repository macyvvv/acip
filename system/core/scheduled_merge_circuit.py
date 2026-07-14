from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system.core.scheduled_merge_control import pause_scheduled_merge

# Counts CONSECUTIVE merge-gate failures across wakes -- any kind (local
# validation failure, path-allowlist violation, stale-base abort, CI not
# green/timeout). A stale-base abort counts too, per ADR-0040's critique
# pass: it's the exact failure mode this repo already hit once for real
# (PR #115 vs #116 needing manual dedup the same session this ADR was
# written), so excluding it from the breaker would leave the one failure
# mode most likely to recur uncounted.
_THRESHOLD = 3


def _state_path(base_path: str | Path = ".") -> Path:
    return Path(base_path) / "system" / "runtime" / "scheduler" / "merge_circuit.json"


def _load(base_path: str | Path) -> dict[str, Any]:
    path = _state_path(base_path)
    if not path.exists():
        return {"consecutive_failures": 0}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"consecutive_failures": 0}
    return payload if isinstance(payload, dict) else {"consecutive_failures": 0}


def _save(base_path: str | Path, state: dict[str, Any]) -> None:
    path = _state_path(base_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def record_merge_gate_failure(reason: str, base_path: str | Path = ".") -> bool:
    """Returns True if this failure tripped the breaker (merge switch paused)."""
    state = _load(base_path)
    state["consecutive_failures"] = int(state.get("consecutive_failures", 0)) + 1
    state["last_failure_reason"] = reason
    state["last_failure_at"] = datetime.now(timezone.utc).isoformat()
    tripped = state["consecutive_failures"] >= _THRESHOLD
    _save(base_path, state)
    if tripped:
        pause_scheduled_merge(
            reason=f"circuit_breaker_tripped: {_THRESHOLD} consecutive merge-gate failures, last={reason}",
            paused_by="circuit_breaker",
            base_path=base_path,
        )
        state["consecutive_failures"] = 0
        _save(base_path, state)
    return tripped


def record_merge_gate_success(base_path: str | Path = ".") -> None:
    state = _load(base_path)
    if state.get("consecutive_failures", 0) == 0:
        return
    state["consecutive_failures"] = 0
    _save(base_path, state)
