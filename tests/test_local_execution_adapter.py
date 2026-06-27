from __future__ import annotations

import json
from pathlib import Path

from orchestrator.local_execution_adapter import LocalExecutionAdapter


def test_local_execution_adapter_dry_run(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({
            "request_id": "REQ-ACCEPTANCE-0001",
            "request_status": "ready",
            "request_priority": 100,
            "approval_required": False,
            "dependency": ["runtime/supervisor/latest.json"],
            "worker_assignment": "Codex",
            "next_action": "Issue #28: ACCEPTANCE-0001: Single Product Vertical Slice",
            "objective": "Constitution v3 Freeze",
            "candidate_source": [],
            "issue_number": 28,
        }),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Constitution v3 Freeze"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}), encoding="utf-8")
    adapter = LocalExecutionAdapter(tmp_path)
    result = adapter.run(dry_run=True)
    assert result.adapter_mode == "dry_run"
    assert result.execution_gate == "closed"
    assert result.request_id == "REQ-ACCEPTANCE-0001"
    assert result.codex_cli_command.startswith("codex --dry-run")
    assert (tmp_path / "runtime" / "local_execution" / "latest.json").exists()
