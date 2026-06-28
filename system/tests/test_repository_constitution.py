from __future__ import annotations

import json
from pathlib import Path


def test_repository_constitution_is_stable() -> None:
    payload = json.loads(Path("runtime/repository_constitution/constitution.json").read_text(encoding="utf-8"))
    assert payload["status"] == "stable"
    assert len(payload["principles"]) == 10
