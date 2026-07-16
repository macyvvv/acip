from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from system.core.statistics_engine import (
    InvalidStudyError,
    power_two_proportion,
    sample_size_for_proportion_ci,
    srm_check,
    validate_study_config,
    wilson_confidence_interval,
)


def _valid_study() -> dict[str, object]:
    return {
        "population": "target stores",
        "frame": {"description": "consented stores", "coverage_limitations": ["offline-only stores excluded"]},
        "estimand": {"kind": "proportion", "target": "conversion rate"},
        "primary_metric": {"name": "conversion", "formula": "orders/visits", "window": "14d", "timezone": "Asia/Tokyo"},
        "precision": {"kind": "ci_half_width", "value": 0.05},
        "stopping": {"rule": "fixed_n", "decision_boundary": "n>=385"},
        "sample_size_method": {"library": "statistics_engine", "version": "v1", "inputs": {"half_width": 0.05}},
        "missingness": "dropouts reported separately",
        "analysis_code_version": "abcdef0",
    }


def test_sample_size_matches_worst_case_proportion_benchmark() -> None:
    assert sample_size_for_proportion_ci(0.05, confidence_level=0.95, proportion=0.5) == 385


def test_wilson_interval_matches_reference_tolerance() -> None:
    interval = wilson_confidence_interval(42, 100, confidence_level=0.95)
    assert abs(interval.lower - 0.328) < 0.01
    assert abs(interval.upper - 0.519) < 0.01
    assert interval.estimate == 0.42


def test_power_calculation_hits_reference_range() -> None:
    power = power_two_proportion(0.10, 0.15, sample_size_per_arm=685, alpha=0.05)
    assert 0.79 <= power <= 0.83


def test_srm_detects_invalid_assignment() -> None:
    result = srm_check([650, 350], [0.5, 0.5], alpha=0.01)
    assert result.chi_square > 80
    assert result.p_value < 1e-10
    assert result.is_valid is False


def test_srm_accepts_balanced_assignment() -> None:
    result = srm_check([502, 498], [0.5, 0.5], alpha=0.01)
    assert result.p_value > 0.5
    assert result.is_valid is True


def test_invalid_study_is_blocked_on_missing_protocol_fields() -> None:
    study = _valid_study()
    study.pop("population")
    try:
        validate_study_config(study)
    except InvalidStudyError as exc:
        assert "population" in str(exc)
    else:
        raise AssertionError("missing population should block study")


def test_invalid_study_is_blocked_on_missing_sample_size_version() -> None:
    study = _valid_study()
    study["sample_size_method"] = {"library": "statistics_engine", "inputs": {"half_width": 0.05}}
    try:
        validate_study_config(study)
    except InvalidStudyError as exc:
        assert "library and version" in str(exc)
    else:
        raise AssertionError("missing sample size version should block study")
