from __future__ import annotations

import json
from pathlib import Path


def test_generated_artifact_registry_lists_expected_artifacts() -> None:
    registry = json.loads(Path("runtime/generated_artifacts/generated_artifacts.json").read_text(encoding="utf-8"))
    assert "graph/repository_graph.json" in registry["generated_artifacts"]
    assert "runtime/validation/validation_report.json" in registry["generated_artifacts"]
