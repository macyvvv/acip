from __future__ import annotations

from orchestrator.runtime_artifact_policy import RuntimeArtifactWritePolicy


def test_runtime_artifact_policy_requires_explicit_refresh() -> None:
    policy = RuntimeArtifactWritePolicy(registry=("runtime/validation/validation_report.json",))
    assert policy.can_write("runtime/validation/validation_report.json") is False
    assert policy.can_write("runtime/validation/validation_report.json", explicit_refresh=True) is True
