from __future__ import annotations

from system.orchestrator.runtime_artifact_policy import RuntimeArtifactWritePolicy


def test_runtime_artifact_policy_requires_explicit_refresh() -> None:
    policy = RuntimeArtifactWritePolicy(registry=("system/runtime/validation/validation_report.json",))
    assert policy.can_write("system/runtime/validation/validation_report.json") is False
    assert policy.can_write("system/runtime/validation/validation_report.json", explicit_refresh=True) is True
