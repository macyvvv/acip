from __future__ import annotations

import json
from pathlib import Path

from orchestrator.local_supervisor import LocalSupervisor


def test_local_supervisor_writes_runtime(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"mission":"Build","current_objective":"Publish","current_pack":"PACK-0011","current_ep":"EP-0187","approved_next_action":"draft","parking_lot":[],"refactoring_priorities":[],"blocked_items":[],"approval_required":False}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health":"healthy","approval_required":False,"next_action":"draft"}), encoding="utf-8")
    supervisor = LocalSupervisor(tmp_path)
    result = supervisor.run(execution_flag=False)
    assert result.execution_mode == "dry_run"
    assert (tmp_path / "runtime" / "supervisor" / "latest.json").exists()
