from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.work_planner import WorkPlanner


def test_work_planner_builds_candidates(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission": "Build an AI Native Company.", "current_phase": "GitHub Foundation", "current_objective": "Constitution v3 Freeze"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"approval_required": False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_constitution").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_constitution" / "constitution.json").write_text(json.dumps({"status": "stable"}), encoding="utf-8")
    planner = WorkPlanner(tmp_path)
    plan = planner.build()
    assert plan.candidate_items[0].candidate_id == "WP-0194"
    assert plan.candidate_items[-1].approval_required is False
    planner.write(plan)
    assert (tmp_path / "runtime" / "work_planner" / "latest.json").exists()
