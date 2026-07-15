from __future__ import annotations

from system.orchestrator.root_inventory import RootInventory


def test_root_inventory_classifies_entries() -> None:
    inventory = RootInventory('.').classify()
    assert inventory
