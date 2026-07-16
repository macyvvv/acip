from __future__ import annotations

from dataclasses import dataclass
from math import erf, erfc, sqrt
from statistics import NormalDist
from typing import Any


_NORMAL = NormalDist()


class InvalidStudyError(ValueError):
    pass


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float
    level: float
    estimate: float


@dataclass(frozen=True)
class SRMResult:
    chi_square: float
    p_value: float
    is_valid: bool


def validate_study_config(study: dict[str, Any]) -> None:
    required = (
        "population",
        "frame",
        "estimand",
        "primary_metric",
        "precision",
        "stopping",
        "sample_size_method",
        "missingness",
        "analysis_code_version",
    )
    missing = [field for field in required if field not in study]
    if missing:
        raise InvalidStudyError(f"missing required study fields: {', '.join(missing)}")
    method = study["sample_size_method"]
    if not isinstance(method, dict) or not method.get("library") or not method.get("version"):
        raise InvalidStudyError("sample_size_method must include library and version")
    precision = study["precision"]
    if not isinstance(precision, dict) or precision.get("value", 0) <= 0:
        raise InvalidStudyError("precision.value must be > 0")


def z_value(confidence_level: float) -> float:
    return _NORMAL.inv_cdf((1.0 + confidence_level) / 2.0)


def sample_size_for_proportion_ci(half_width: float, confidence_level: float = 0.95, proportion: float = 0.5) -> int:
    if not 0 < half_width < 1:
        raise ValueError("half_width must be between 0 and 1")
    if not 0 < proportion < 1:
        raise ValueError("proportion must be between 0 and 1")
    z = z_value(confidence_level)
    n = (z * z * proportion * (1.0 - proportion)) / (half_width * half_width)
    return int(n) if n.is_integer() else int(n) + 1


def wilson_confidence_interval(successes: int, trials: int, confidence_level: float = 0.95) -> ConfidenceInterval:
    if trials <= 0:
        raise ValueError("trials must be positive")
    if not 0 <= successes <= trials:
        raise ValueError("successes must be between 0 and trials")
    z = z_value(confidence_level)
    p = successes / trials
    denom = 1.0 + (z * z) / trials
    center = (p + (z * z) / (2.0 * trials)) / denom
    margin = (z / denom) * sqrt((p * (1.0 - p) / trials) + ((z * z) / (4.0 * trials * trials)))
    return ConfidenceInterval(lower=max(0.0, center - margin), upper=min(1.0, center + margin), level=confidence_level, estimate=p)


def power_two_proportion(control_rate: float, treatment_rate: float, sample_size_per_arm: int, alpha: float = 0.05) -> float:
    if sample_size_per_arm <= 0:
        raise ValueError("sample_size_per_arm must be positive")
    if not 0 < control_rate < 1 or not 0 < treatment_rate < 1:
        raise ValueError("rates must be between 0 and 1")
    pooled = (control_rate + treatment_rate) / 2.0
    effect = abs(treatment_rate - control_rate)
    se0 = sqrt(2.0 * pooled * (1.0 - pooled) / sample_size_per_arm)
    se1 = sqrt(
        (control_rate * (1.0 - control_rate) + treatment_rate * (1.0 - treatment_rate)) / sample_size_per_arm
    )
    z_alpha = z_value(1.0 - alpha)
    z_effect = (effect - z_alpha * se0) / se1
    return max(0.0, min(1.0, _NORMAL.cdf(z_effect)))


def srm_check(observed: list[int], expected_proportions: list[float], alpha: float = 0.01) -> SRMResult:
    if len(observed) != len(expected_proportions) or not observed:
        raise ValueError("observed and expected_proportions must have equal non-zero length")
    total = sum(observed)
    if total <= 0:
        raise ValueError("observed total must be positive")
    if abs(sum(expected_proportions) - 1.0) > 1e-9:
        raise ValueError("expected_proportions must sum to 1")
    chi_square = 0.0
    for count, proportion in zip(observed, expected_proportions):
        expected = total * proportion
        if expected <= 0:
            raise ValueError("expected counts must be positive")
        chi_square += ((count - expected) ** 2) / expected
    degrees_of_freedom = len(observed) - 1
    if degrees_of_freedom != 1:
        # Conservative upper bound via normal approximation for current Phase -1 use.
        standardized = (chi_square - degrees_of_freedom) / sqrt(2.0 * degrees_of_freedom)
        p_value = 1.0 - _NORMAL.cdf(standardized)
    else:
        p_value = erfc(sqrt(chi_square / 2.0))
    return SRMResult(chi_square=chi_square, p_value=p_value, is_valid=p_value >= alpha)
