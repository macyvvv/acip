from __future__ import annotations

from pathlib import Path

from system.core.scheduled_merge_circuit import (
    _THRESHOLD,
    record_merge_gate_failure,
    record_merge_gate_success,
)
from system.core.scheduled_merge_control import is_scheduled_merge_paused, scheduled_merge_pause_info


def test_failures_below_threshold_do_not_pause(tmp_path: Path) -> None:
    for _ in range(_THRESHOLD - 1):
        tripped = record_merge_gate_failure("stale_base_abort", tmp_path)
        assert tripped is False
    assert is_scheduled_merge_paused(tmp_path) is False


def test_threshold_consecutive_failures_trips_the_breaker(tmp_path: Path) -> None:
    for _ in range(_THRESHOLD - 1):
        record_merge_gate_failure("stale_base_abort", tmp_path)
    tripped = record_merge_gate_failure("stale_base_abort", tmp_path)
    assert tripped is True
    assert is_scheduled_merge_paused(tmp_path) is True
    info = scheduled_merge_pause_info(tmp_path)
    assert info["paused_by"] == "circuit_breaker"
    assert "stale_base_abort" in info["reason"]


def test_a_success_resets_the_consecutive_counter(tmp_path: Path) -> None:
    for _ in range(_THRESHOLD - 1):
        record_merge_gate_failure("local_pytest_failed", tmp_path)
    record_merge_gate_success(tmp_path)
    # Counter reset -- another THRESHOLD-1 failures alone must not trip it.
    for _ in range(_THRESHOLD - 1):
        tripped = record_merge_gate_failure("local_pytest_failed", tmp_path)
        assert tripped is False
    assert is_scheduled_merge_paused(tmp_path) is False


def test_different_failure_reasons_all_count_toward_the_same_breaker(tmp_path: Path) -> None:
    # A stale-base abort must count the same as a validation failure -- this
    # is the exact failure mode ADR-0040's critique pass flagged as the one
    # most likely to recur (PR #115 vs #116 needing manual dedup the same
    # session this ADR was written), so it must not be excluded.
    record_merge_gate_failure("diff_outside_allowlist:some/path", tmp_path)
    record_merge_gate_failure("local_validate_all_failed", tmp_path)
    tripped = record_merge_gate_failure("stale_base_abort", tmp_path)
    assert tripped is True
