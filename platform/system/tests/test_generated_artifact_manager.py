from __future__ import annotations

from system.orchestrator.generated_artifact_manager import GeneratedArtifactManager


def test_generated_artifact_manager_classifies_dirty_paths() -> None:
    manager = GeneratedArtifactManager(".")
    report = manager.report_dirty(["graph/repository_graph.json", "platform/docs/current/GENERATED_ARTIFACTS.md", "manual.txt"])
    assert "manual.txt" in report.manual_dirty

