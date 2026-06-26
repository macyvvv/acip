from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalTriggerDryRunValidationResult:
    passed: bool
    reason: str
