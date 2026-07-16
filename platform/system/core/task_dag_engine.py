from __future__ import annotations

from dataclasses import dataclass
import errno
import json
import os
from pathlib import Path
from typing import Any


class DagStateError(ValueError):
    pass


class InvalidTransitionError(DagStateError):
    pass


class ClaimConflictError(DagStateError):
    pass


# Mirrors businesses/cf_gb_relative_system/artifacts/E-004A/output.json --
# the two must be kept in sync by hand; there is no single source of truth
# file both sides load, since the contract artifact is JSON evidence and
# this module is the runtime implementation of it.
ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "blocked": ("ready", "quarantined"),
    "ready": ("running", "quarantined"),
    "running": ("succeeded", "failed", "quarantined"),
    "failed": ("ready", "quarantined"),
    "succeeded": (),
    "quarantined": ("ready",),
}


@dataclass(frozen=True)
class ClaimRecord:
    business_id: str
    task_id: str
    manifest_version: str
    worker_id: str
    idempotency_key: str


def validate_transition(current_state: str, next_state: str) -> None:
    if current_state not in ALLOWED_TRANSITIONS:
        raise InvalidTransitionError(f"Unknown current_state '{current_state}'")
    if next_state not in ALLOWED_TRANSITIONS[current_state]:
        raise InvalidTransitionError(
            f"Transition '{current_state}' -> '{next_state}' is not allowed; "
            f"allowed next states are {ALLOWED_TRANSITIONS[current_state]}"
        )


def compute_ready_tasks(tasks: list[dict[str, Any]]) -> list[str]:
    """Pure function: which currently-blocked tasks have every dependency
    succeeded and should release to ready. Does not mutate task state --
    callers apply the transition (through validate_transition) themselves."""
    state_by_id = {task["id"]: task["state"] for task in tasks}
    newly_ready = []
    for task in tasks:
        if task["state"] != "blocked":
            continue
        depends = task.get("depends", [])
        if all(state_by_id.get(dep) == "succeeded" for dep in depends):
            newly_ready.append(task["id"])
    return newly_ready


def _claim_dir(business_id: str, state_dir: str | Path) -> Path:
    return Path(state_dir) / business_id / "claims"


def _claim_path(business_id: str, task_id: str, state_dir: str | Path) -> Path:
    return _claim_dir(business_id, state_dir) / f"{task_id}.claim.json"


def claim_task(
    *,
    business_id: str,
    task_id: str,
    manifest_version: str,
    worker_id: str,
    current_state: str,
    state_dir: str | Path,
) -> ClaimRecord:
    """Atomically transitions ready -> running. Fails closed: an invalid
    source state is rejected before any filesystem write is attempted, and
    the claim file itself is created with O_CREAT|O_EXCL so two concurrent
    claims for the same (business_id, task_id, manifest_version) can never
    both succeed -- the loser gets ClaimConflictError, never a silently
    overwritten claim."""
    validate_transition(current_state, "running")
    idempotency_key = f"{business_id}:{task_id}:{manifest_version}"
    record = ClaimRecord(
        business_id=business_id,
        task_id=task_id,
        manifest_version=manifest_version,
        worker_id=worker_id,
        idempotency_key=idempotency_key,
    )
    claim_dir = _claim_dir(business_id, state_dir)
    claim_dir.mkdir(parents=True, exist_ok=True)
    claim_path = _claim_path(business_id, task_id, state_dir)
    payload = json.dumps(
        {
            "business_id": record.business_id,
            "task_id": record.task_id,
            "manifest_version": record.manifest_version,
            "worker_id": record.worker_id,
            "idempotency_key": record.idempotency_key,
        }
    )
    try:
        fd = os.open(claim_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        existing = json.loads(claim_path.read_text())
        raise ClaimConflictError(
            f"Task '{task_id}' is already claimed by worker '{existing['worker_id']}' "
            f"(idempotency_key={existing['idempotency_key']})"
        ) from exc
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            raise ClaimConflictError(f"Task '{task_id}' is already claimed") from exc
        raise
    with os.fdopen(fd, "w") as handle:
        handle.write(payload)
    return record


def complete_task(
    *,
    business_id: str,
    task_id: str,
    worker_id: str,
    next_state: str,
    state_dir: str | Path,
) -> None:
    """Transitions running -> {succeeded, failed, quarantined}. Requires the
    caller to hold the claim written by claim_task -- a worker_id mismatch
    means a different worker is trying to complete a task it never claimed,
    which is rejected rather than silently honored."""
    validate_transition("running", next_state)
    claim_path = _claim_path(business_id, task_id, state_dir)
    if not claim_path.exists():
        raise DagStateError(f"Task '{task_id}' has no active claim to complete")
    existing = json.loads(claim_path.read_text())
    if existing["worker_id"] != worker_id:
        raise ClaimConflictError(
            f"Task '{task_id}' is claimed by worker '{existing['worker_id']}', not '{worker_id}'"
        )
    claim_path.unlink()


def release_stale_claim(*, business_id: str, task_id: str, state_dir: str | Path) -> None:
    """Recovery path for E-004C (retry/resume) -- deletes an orphaned claim
    file so the task can be reclaimed. Deliberately does not decide
    staleness itself (no wall-clock reads here); the caller supplies that
    judgment."""
    claim_path = _claim_path(business_id, task_id, state_dir)
    if claim_path.exists():
        claim_path.unlink()
