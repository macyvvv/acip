from __future__ import annotations

from pathlib import Path

import pytest

from system.core.execution_pre_approval_state import (
    ExecutionPreApprovalAlreadyInFlightError,
    ExecutionPreApprovalCapExceededError,
    ExecutionPreApprovalStateError,
    claim_pre_approval,
    counts_for_today,
    counts_for_week,
    mark_pre_approval_outcome,
)


def test_fresh_claim_consumes_cap_slot(tmp_path: Path) -> None:
    result = claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    assert result == "claimed"
    assert counts_for_today("text_syndicate", "market_research", tmp_path) == 1
    assert counts_for_week("text_syndicate", "market_research", tmp_path) == 1


def test_second_claim_while_in_flight_raises(tmp_path: Path) -> None:
    claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    with pytest.raises(ExecutionPreApprovalAlreadyInFlightError):
        claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    # In-flight claim must not have consumed a second slot
    assert counts_for_today("text_syndicate", "market_research", tmp_path) == 1


def test_claim_on_completed_task_returns_already_completed_no_recount(tmp_path: Path) -> None:
    claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    mark_pre_approval_outcome("text_syndicate", "market_research", "task-0001", True, tmp_path)
    result = claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    assert result == "already_completed"
    assert counts_for_today("text_syndicate", "market_research", tmp_path) == 1


def test_failed_task_can_be_reclaimed_without_second_cap_charge(tmp_path: Path) -> None:
    claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    mark_pre_approval_outcome("text_syndicate", "market_research", "task-0001", False, tmp_path)
    result = claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    assert result == "claimed"
    assert counts_for_today("text_syndicate", "market_research", tmp_path) == 1


def test_cap_exceeded_on_new_task_id_once_at_limit(tmp_path: Path) -> None:
    claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 1, None, tmp_path)
    mark_pre_approval_outcome("text_syndicate", "market_research", "task-0001", True, tmp_path)
    with pytest.raises(ExecutionPreApprovalCapExceededError):
        claim_pre_approval("text_syndicate", "market_research", "task-0002", "POL-1", 1, None, tmp_path)


def test_weekly_cap_exceeded(tmp_path: Path) -> None:
    claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 10, 1, tmp_path)
    mark_pre_approval_outcome("text_syndicate", "market_research", "task-0001", True, tmp_path)
    with pytest.raises(ExecutionPreApprovalCapExceededError):
        claim_pre_approval("text_syndicate", "market_research", "task-0002", "POL-1", 10, 1, tmp_path)


def test_stale_claim_can_be_reclaimed(tmp_path: Path, monkeypatch) -> None:
    import system.core.execution_pre_approval_state as module
    from datetime import timedelta

    claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)

    # Simulate time passing well beyond the staleness window without ever
    # calling mark_pre_approval_outcome (a crash-mid-execution scenario).
    # Scoped to only the reclaim call (monkeypatch.context(), not the whole
    # test) -- freezing time for the entire test made this genuinely flaky
    # near a UTC day boundary: counts_for_today()'s day-key is real-time-
    # based, so asserting against it while +20 minutes had already crossed
    # into the next UTC day looked up the wrong day's counter (found live,
    # reproduced consistently while it was ~23:5x UTC).
    real_datetime = module.datetime

    class _FrozenFuture(real_datetime):
        @classmethod
        def now(cls, tz=None):
            return real_datetime.now(tz) + timedelta(minutes=20)

    with monkeypatch.context() as m:
        m.setattr(module, "datetime", _FrozenFuture)
        result = claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 3, 10, tmp_path)
    assert result == "claimed"
    # Recovery re-claim must not consume a second cap slot -- checked with
    # the real clock restored, matching the real day the original claim's
    # counter was actually written under.
    assert counts_for_today("text_syndicate", "market_research", tmp_path) == 1


def test_shard_isolation_across_business_and_role(tmp_path: Path) -> None:
    claim_pre_approval("text_syndicate", "market_research", "task-0001", "POL-1", 1, None, tmp_path)
    # A different role for the same business, and the same role for a
    # different business, must have entirely independent state.
    assert claim_pre_approval("text_syndicate", "marketing", "task-0001", "POL-2", 1, None, tmp_path) == "claimed"
    assert claim_pre_approval("kabukicho_survival_map", "market_research", "task-0001", "POL-3", 1, None, tmp_path) == "claimed"


def test_mark_outcome_without_prior_claim_raises(tmp_path: Path) -> None:
    with pytest.raises(ExecutionPreApprovalStateError):
        mark_pre_approval_outcome("text_syndicate", "market_research", "task-9999", True, tmp_path)


def test_corrupted_state_file_hard_fails(tmp_path: Path) -> None:
    path = tmp_path / "system/runtime/agent_handoff/pre_approval_state/text_syndicate/market_research/state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json")
    with pytest.raises(ExecutionPreApprovalStateError):
        counts_for_today("text_syndicate", "market_research", tmp_path)
    with pytest.raises(ExecutionPreApprovalStateError):
        claim_pre_approval("text_syndicate", "market_research", "task-0002", "POL-1", 3, 10, tmp_path)
