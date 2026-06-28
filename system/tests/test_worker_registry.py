from pathlib import Path

import pytest

from workers.registry import WorkerRegistryError, load_worker_registry


def test_load_worker_registry() -> None:
    registry = load_worker_registry()
    codex = registry.get("Codex")
    assert "repository_implementation" in codex.capability
    assert "validate" in codex.allowed_actions
    assert "approve" not in codex.allowed_actions


def test_missing_worker_fails(tmp_path: Path) -> None:
    registry_file = tmp_path / "registry.yaml"
    registry_file.write_text("workers: {}", encoding="utf-8")

    with pytest.raises(WorkerRegistryError, match="Missing required workers"):
        load_worker_registry(registry_file)
