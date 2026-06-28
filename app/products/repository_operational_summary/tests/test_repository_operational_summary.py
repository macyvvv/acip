from __future__ import annotations

import json
from pathlib import Path

from product.repository_operational_summary.src.repository_operational_summary import load_summary, render_summary


def test_render_summary(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(
        json.dumps({"mission": "Build an AI Native Company.", "current_objective": "Constitution v3 Freeze"}),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(
        json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}),
        encoding="utf-8",
    )
    summary = load_summary(tmp_path)
    rendered = render_summary(summary)
    assert "Repository Operational Summary" in rendered
    assert "Current objective: Constitution v3 Freeze" in rendered
    assert "Approval required: false" in rendered
