from __future__ import annotations

from orchestrator.pack_manager import PackManager


def test_solution_development_pack_is_registered() -> None:
    packs = PackManager(".").load_registry()
    assert any(pack.pack_id == "PACK-0001" for pack in packs)
