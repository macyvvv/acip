from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.repository_state_builder import RepositoryStateBuilder


def test_repository_state_builder_writes_projection(tmp_path: Path) -> None:
    (tmp_path / "docs" / "current").mkdir(parents=True)
    (tmp_path / "docs" / "current" / "QUEUE_STATE.md").write_text("# QUEUE_STATE\n\nstatus: READY\nactive_ep: EP-9999\nnext_ep: EP-9998\n", encoding="utf-8")
    (tmp_path / "docs" / "current" / "VALIDATION_STATE.md").write_text("# VALIDATION_STATE\n\nlast_validation_status: success\nlast_validation_command: python platform/system/scripts/validate_all.py\nlast_validation_report_json: platform/system/runtime/validation/validation_report.json\nlast_validation_report_md: platform/system/runtime/validation/VALIDATION_REPORT.md\nvalidation_owner: Codex\nrerun_required_when:\n  - any validation step fails\nhuman_rerun_policy: Human reruns validation only when repository outputs changed.\nrelation_to_worker_output_contract: Validation state is a repository-level summary.\n", encoding="utf-8")
    (tmp_path / "runtime" / "handoff").mkdir(parents=True)
    (tmp_path / "runtime" / "handoff" / "latest.json").write_text(json.dumps({"status":"success","pack_id":"PACK-0004","ep_id":"EP-0160","worktree_state":"clean","next_action":"review","requires_human_approval":False}), encoding="utf-8")
    (tmp_path / "runtime" / "handoff" / "completion").mkdir(parents=True, exist_ok=True)
    (tmp_path / "runtime" / "handoff" / "completion" / "latest.json").write_text(json.dumps({"status":"success","pack_id":"PACK-0004","ep_id":"EP-0160","worktree_state":"clean","next_action":"review","requires_human_approval":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_constitution").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_constitution" / "constitution.json").write_text('{"status":"stable","principles":["a","b","c","d","e","f","g","h","i","j"]}', encoding="utf-8")
    (tmp_path / "runtime" / "event_runtime").mkdir(parents=True)
    (tmp_path / "runtime" / "event_runtime" / "dry_run.json").write_text('{}', encoding='utf-8')
    (tmp_path / "packs").mkdir(exist_ok=True)
    (tmp_path / "packs" / "registry.yaml").write_text('- pack_id: PACK-0004\n- pack_id: PACK-0005\n', encoding='utf-8')
    (tmp_path / "docs" / "current" / "PACK_0005_EXECUTION_RECORD.md").write_text('# PACK_0005_EXECUTION_RECORD\n', encoding='utf-8')
    (tmp_path / "docs" / "current" / "PACK_0003_EXECUTION_RECORD.md").write_text('# PACK_0003_EXECUTION_RECORD\n', encoding='utf-8')
    builder = RepositoryStateBuilder(tmp_path)
    state = builder.build()
    assert state.active_pack == 'PACK-0004'
    builder.write(state)
    assert (tmp_path / 'runtime' / 'repository_state' / 'latest.json').exists()
