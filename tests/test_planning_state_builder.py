from __future__ import annotations

import json
from pathlib import Path

from orchestrator.planning_state_builder import PlanningStateBuilder


def test_planning_state_builder_writes_projection(tmp_path: Path) -> None:
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "docs" / "current" / "PROJECT.md").write_text("# PROJECT\n\n## Mission\n\nBuild an AI Native Company.\n\n## Vision\n\nKnowledge First\n\n## Current Phase\n\nPhase 0\n\n## Current Objective\n\nConstitution v3 Freeze\n", encoding="utf-8")
    (tmp_path / "docs" / "current" / "STATE.md").write_text("# STATE\n\n## Current Phase\n\nPhase 1 : Knowledge Layer Design\n\n## Current Objective\n\nKnowledge Repository\n", encoding="utf-8")
    (tmp_path / "docs" / "current" / "ROADMAP.md").write_text("# ROADMAP\n\n## Phase 0\n\n- GitHub foundation\n", encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"active_pack":"PACK-0004","active_ep":"EP-0160","queue_status":"READY","validation_status":"success","pytest_status":"success","worktree_state":"clean","approval_required":False,"next_action":"review","latest_completion":{}}, indent=2), encoding="utf-8")
    (tmp_path / "runtime" / "repository_constitution").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_constitution" / "constitution.json").write_text('{"status":"stable","principles":["a","b","c","d","e","f","g","h","i","j"]}', encoding="utf-8")
    (tmp_path / "runtime" / "validation").mkdir(parents=True)
    (tmp_path / "runtime" / "validation" / "validation_report.json").write_text('{"overall_success": true}', encoding='utf-8')
    (tmp_path / "runtime" / "handoff").mkdir(parents=True)
    (tmp_path / "runtime" / "handoff" / "latest.json").write_text(json.dumps({"status":"success","pack_id":"PACK-0004","ep_id":"EP-0160","worktree_state":"clean","next_action":"review","requires_human_approval":False}), encoding='utf-8')
    (tmp_path / "runtime" / "handoff" / "completion").mkdir(parents=True, exist_ok=True)
    (tmp_path / "runtime" / "handoff" / "completion" / "latest.json").write_text(json.dumps({"status":"success","pack_id":"PACK-0004","ep_id":"EP-0160","worktree_state":"clean","next_action":"review","requires_human_approval":False}), encoding='utf-8')
    (tmp_path / "packs").mkdir(exist_ok=True)
    (tmp_path / "packs" / "registry.yaml").write_text('- pack_id: PACK-0004\n', encoding='utf-8')
    (tmp_path / "wbs").mkdir(exist_ok=True)
    (tmp_path / "wbs" / "WBS-0001.md").write_text('# WBS-0001\n', encoding='utf-8')
    builder = PlanningStateBuilder(tmp_path)
    state = builder.build()
    assert state.mission == 'Build an AI Native Company.'
    builder.write(state)
    assert (tmp_path / 'runtime' / 'planning' / 'latest.json').exists()
