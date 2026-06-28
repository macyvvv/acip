from __future__ import annotations

import json
from pathlib import Path


def test_first_product_projection(tmp_path: Path) -> None:
    planning = tmp_path / "runtime" / "planning"
    planning.mkdir(parents=True)
    planning.joinpath("first_product.json").write_text(json.dumps({"objective": "Use Repository OS v2 as the operating system for the first production outcome."}), encoding="utf-8")
    assert json.loads(planning.joinpath("first_product.json").read_text(encoding="utf-8"))["objective"]
