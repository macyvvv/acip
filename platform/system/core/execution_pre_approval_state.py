from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from system.core.file_lock import locked

# Sharded per (business_id, role_id), NOT one shared file -- same reasoning
# as publishing_state.py/ADR-0034/0035: unrelated businesses/roles would
# otherwise contend on one flock, and one corrupted file would take down
# every business's pre-approval capability at once.
#
# This file is the SINGLE SOURCE OF TRUTH for a task's pre-approval
# lifecycle (claimed/completed/failed). An earlier draft split this from a
# separate read of the execution-outcome artifact under
# platform/system/runtime/business_agents/... -- that split created a real
# check-then-act race, since (unlike Level 3c's instant DryRunProvider)
# BusinessAgentExecutionAdapter.run()'s subprocess call is genuinely slow
# (up to 60s). Concurrency safety now depends entirely on this module's
# locked, fresh-read-inside-the-lock critical section.

_STALE_CLAIM_WINDOW = timedelta(minutes=10)  # well past the adapter's 60s default timeout, plus margin


class ExecutionPreApprovalStateError(RuntimeError):
    pass


class ExecutionPreApprovalCapExceededError(ExecutionPreApprovalStateError):
    pass


class ExecutionPreApprovalAlreadyInFlightError(ExecutionPreApprovalStateError):
    pass


def _state_path(business_id: str, role_id: str, base_path: str | Path = ".") -> Path:
    return Path(base_path) / "platform/system/runtime/agent_handoff/pre_approval_state" / business_id / role_id / "state.json"


def _default_state() -> dict[str, Any]:
    return {"tasks": {}, "counters": {}}


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        # Fail closed, not open: corrupted state must never be read as
        # "empty" -- that would silently forget in-flight/completed status
        # and cap counts, the exact direction (re-execute, blow through
        # caps) a safety mechanism must never fail in.
        raise ExecutionPreApprovalStateError(f"{path} is corrupted and could not be parsed: {exc}") from exc
    if not isinstance(data, dict) or "tasks" not in data or "counters" not in data:
        raise ExecutionPreApprovalStateError(f"{path} has an unexpected shape; refusing to treat it as empty")
    return data


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _today_key() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _week_key() -> str:
    iso = datetime.now(timezone.utc).isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def counts_for_today(business_id: str, role_id: str, base_path: str | Path = ".") -> int:
    state = _load_state(_state_path(business_id, role_id, base_path))
    return int(state["counters"].get(_today_key(), 0))


def counts_for_week(business_id: str, role_id: str, base_path: str | Path = ".") -> int:
    state = _load_state(_state_path(business_id, role_id, base_path))
    return int(state["counters"].get(_week_key(), 0))


def claim_pre_approval(
    business_id: str,
    role_id: str,
    task_id: str,
    policy_id: str,
    max_auto_approvals_per_day: int,
    max_auto_approvals_per_week: int | None,
    base_path: str | Path = ".",
) -> str:
    """Returns "claimed" (caller must execute) or "already_completed"
    (caller must skip execution and any downstream chain-trigger). Raises
    ExecutionPreApprovalCapExceededError or ExecutionPreApprovalAlreadyInFlightError."""
    path = _state_path(business_id, role_id, base_path)
    with locked(path):
        state = _load_state(path)  # fresh read INSIDE the critical section
        entry = state["tasks"].get(task_id)
        now = datetime.now(timezone.utc)

        if entry is not None and entry.get("status") == "completed":
            return "already_completed"

        if entry is not None and entry.get("status") == "claimed":
            claimed_at = datetime.fromisoformat(entry["claimed_at"])
            if now - claimed_at < _STALE_CLAIM_WINDOW:
                raise ExecutionPreApprovalAlreadyInFlightError(
                    f"{business_id}/{role_id}/{task_id} was claimed at {entry['claimed_at']} "
                    f"and is still within the in-flight window -- refusing a second concurrent claim"
                )
            # Stale claim: the prior claimer almost certainly crashed without
            # calling mark_pre_approval_outcome. Recoverable by re-claiming,
            # same as a failed-retry -- does not re-touch the counters.

        if entry is not None and entry.get("status") in {"claimed", "failed"}:
            # Retry path (stale-in-flight recovery, or a previously failed
            # attempt): the cap slot was already consumed on first claim: do
            # not check or increment counters again.
            state["tasks"][task_id] = {
                "policy_id": policy_id,
                "status": "claimed",
                "claimed_at": now.isoformat(),
            }
            _write_state(path, state)
            return "claimed"

        # Genuinely new task_id: check caps atomically in this same critical
        # section (never a separate counts_for_today() call beforehand --
        # that would reopen the exact check-then-act race this design closes).
        day_key, week_key = _today_key(), _week_key()
        today_count = int(state["counters"].get(day_key, 0))
        week_count = int(state["counters"].get(week_key, 0))
        if today_count >= max_auto_approvals_per_day:
            raise ExecutionPreApprovalCapExceededError(
                f"{business_id}/{role_id} has reached its daily cap of {max_auto_approvals_per_day}"
            )
        if max_auto_approvals_per_week is not None and week_count >= max_auto_approvals_per_week:
            raise ExecutionPreApprovalCapExceededError(
                f"{business_id}/{role_id} has reached its weekly cap of {max_auto_approvals_per_week}"
            )

        state["tasks"][task_id] = {
            "policy_id": policy_id,
            "status": "claimed",
            "claimed_at": now.isoformat(),
        }
        state["counters"][day_key] = today_count + 1
        state["counters"][week_key] = week_count + 1
        _write_state(path, state)
        return "claimed"


def mark_pre_approval_outcome(
    business_id: str,
    role_id: str,
    task_id: str,
    success: bool,
    base_path: str | Path = ".",
) -> None:
    """Transitions task_id's entry from "claimed" to "completed" (success)
    or "failed" (not success, eligible for retry without a second cap
    charge). Call from a try/finally around the actual adapter invocation --
    a crash mid-execution leaves the entry at "claimed", correctly
    triggering the staleness-recovery path on the next attempt rather than
    "completed" or silently lost."""
    path = _state_path(business_id, role_id, base_path)
    with locked(path):
        state = _load_state(path)
        entry = state["tasks"].get(task_id)
        if entry is None:
            raise ExecutionPreApprovalStateError(
                f"No claim exists for {business_id}/{role_id}/{task_id} -- mark_pre_approval_outcome "
                f"called without a prior claim_pre_approval"
            )
        entry["status"] = "completed" if success else "failed"
        _write_state(path, state)
