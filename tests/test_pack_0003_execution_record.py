from __future__ import annotations

import json
from pathlib import Path


def test_pack_0003_execution_record_maps_child_eps() -> None:
    record = Path("runtime/handoff/completion/latest.json").read_text(encoding="utf-8")
    payload = json.loads(record)
    assert payload["pack_id"] == "PACK-0003"
    assert payload["validation_leaves_worktree_clean_by_default"] is True
