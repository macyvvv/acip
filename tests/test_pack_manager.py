from __future__ import annotations

from orchestrator.pack_manager import PackManager


def test_pack_manager_loads_registry() -> None:
    manager = PackManager(".")
    packs = manager.load_registry()
    assert packs
