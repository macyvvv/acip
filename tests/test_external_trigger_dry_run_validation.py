from __future__ import annotations

from orchestrator.external_trigger_dry_run_validation import ExternalTriggerDryRunValidationResult


def test_external_trigger_dry_run_validation_result() -> None:
    result = ExternalTriggerDryRunValidationResult(True, "ok")
    assert result.passed is True
