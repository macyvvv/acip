from __future__ import annotations

from system.orchestrator.generated_artifact_refresh import GeneratedArtifactRefresh


def test_generated_artifact_refresh_imports() -> None:
    refresh = GeneratedArtifactRefresh(".")
    assert refresh is not None
