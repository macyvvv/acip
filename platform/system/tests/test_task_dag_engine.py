from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from system.core.task_dag_engine import (
    ClaimConflictError,
    DagStateError,
    InvalidTransitionError,
    claim_task,
    compute_ready_tasks,
    complete_task,
    release_stale_claim,
    validate_transition,
)


def _task(task_id: str, state: str, depends: list[str] | None = None) -> dict:
    return {"id": task_id, "state": state, "depends": depends or []}


def test_ready_dependency_release_when_all_deps_succeeded() -> None:
    tasks = [
        _task("A", "succeeded"),
        _task("B", "succeeded"),
        _task("C", "blocked", depends=["A", "B"]),
    ]
    assert compute_ready_tasks(tasks) == ["C"]


def test_ready_dependency_release_withholds_when_dep_not_succeeded() -> None:
    tasks = [
        _task("A", "succeeded"),
        _task("B", "running"),
        _task("C", "blocked", depends=["A", "B"]),
    ]
    assert compute_ready_tasks(tasks) == []


def test_ready_dependency_release_ignores_non_blocked_tasks() -> None:
    tasks = [
        _task("A", "succeeded"),
        _task("B", "ready", depends=["A"]),
        _task("C", "succeeded", depends=["A"]),
    ]
    assert compute_ready_tasks(tasks) == []


def test_valid_transitions_pass() -> None:
    validate_transition("blocked", "ready")
    validate_transition("ready", "running")
    validate_transition("running", "succeeded")
    validate_transition("running", "failed")
    validate_transition("failed", "ready")
    validate_transition("quarantined", "ready")


@pytest.mark.parametrize(
    "current,attempted",
    [
        ("blocked", "succeeded"),
        ("blocked", "running"),
        ("ready", "succeeded"),
        ("succeeded", "ready"),
        ("succeeded", "running"),
        ("failed", "succeeded"),
    ],
)
def test_invalid_transition_rejected(current: str, attempted: str) -> None:
    with pytest.raises(InvalidTransitionError):
        validate_transition(current, attempted)


def test_unknown_state_rejected() -> None:
    with pytest.raises(InvalidTransitionError):
        validate_transition("not_a_real_state", "ready")


def test_claim_task_requires_ready_source_state(tmp_path) -> None:
    with pytest.raises(InvalidTransitionError):
        claim_task(
            business_id="cf_gb_relative_system",
            task_id="E-004B",
            manifest_version="1.0",
            worker_id="worker-1",
            current_state="blocked",
            state_dir=tmp_path,
        )


def test_claim_task_succeeds_from_ready(tmp_path) -> None:
    record = claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-1",
        current_state="ready",
        state_dir=tmp_path,
    )
    assert record.idempotency_key == "cf_gb_relative_system:E-004B:1.0"
    assert (tmp_path / "cf_gb_relative_system" / "claims" / "E-004B.claim.json").exists()


def test_atomic_claim_second_concurrent_claim_is_rejected(tmp_path) -> None:
    claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-1",
        current_state="ready",
        state_dir=tmp_path,
    )
    with pytest.raises(ClaimConflictError):
        claim_task(
            business_id="cf_gb_relative_system",
            task_id="E-004B",
            manifest_version="1.0",
            worker_id="worker-2",
            current_state="ready",
            state_dir=tmp_path,
        )


def test_atomic_claim_isolated_per_task_and_business(tmp_path) -> None:
    claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-1",
        current_state="ready",
        state_dir=tmp_path,
    )
    # Different task_id: independent claim, must succeed.
    other_task = claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-009E",
        manifest_version="1.0",
        worker_id="worker-2",
        current_state="ready",
        state_dir=tmp_path,
    )
    assert other_task.task_id == "E-009E"
    # Different business_id, same task_id: independent claim, must succeed.
    other_business = claim_task(
        business_id="kabukicho_survival_map",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-3",
        current_state="ready",
        state_dir=tmp_path,
    )
    assert other_business.business_id == "kabukicho_survival_map"


def test_complete_task_transitions_running_to_succeeded(tmp_path) -> None:
    claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-1",
        current_state="ready",
        state_dir=tmp_path,
    )
    complete_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        worker_id="worker-1",
        next_state="succeeded",
        state_dir=tmp_path,
    )
    assert not (tmp_path / "cf_gb_relative_system" / "claims" / "E-004B.claim.json").exists()


def test_complete_task_rejects_invalid_next_state(tmp_path) -> None:
    claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-1",
        current_state="ready",
        state_dir=tmp_path,
    )
    with pytest.raises(InvalidTransitionError):
        complete_task(
            business_id="cf_gb_relative_system",
            task_id="E-004B",
            worker_id="worker-1",
            next_state="blocked",
            state_dir=tmp_path,
        )


def test_complete_task_rejects_wrong_worker(tmp_path) -> None:
    claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-1",
        current_state="ready",
        state_dir=tmp_path,
    )
    with pytest.raises(ClaimConflictError):
        complete_task(
            business_id="cf_gb_relative_system",
            task_id="E-004B",
            worker_id="worker-2",
            next_state="succeeded",
            state_dir=tmp_path,
        )


def test_complete_task_without_claim_raises(tmp_path) -> None:
    with pytest.raises(DagStateError):
        complete_task(
            business_id="cf_gb_relative_system",
            task_id="E-004B",
            worker_id="worker-1",
            next_state="succeeded",
            state_dir=tmp_path,
        )


def test_release_stale_claim_allows_reclaim(tmp_path) -> None:
    claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-1",
        current_state="ready",
        state_dir=tmp_path,
    )
    release_stale_claim(business_id="cf_gb_relative_system", task_id="E-004B", state_dir=tmp_path)
    record = claim_task(
        business_id="cf_gb_relative_system",
        task_id="E-004B",
        manifest_version="1.0",
        worker_id="worker-2",
        current_state="ready",
        state_dir=tmp_path,
    )
    assert record.worker_id == "worker-2"
