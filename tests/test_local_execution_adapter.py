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
    assert result.codex_cli_command == 'codex exec -m gpt-5.2-mini "$(cat runtime/local_execution/codex_prompt.md)"'
    assert (tmp_path / "runtime" / "local_execution" / "codex_prompt.md").exists()
    assert (tmp_path / "runtime" / "local_execution" / "latest.json").exists()


def test_local_execution_model_resolution_default(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({"request_id": "REQ-1", "request_status": "ready", "next_action": "Issue #28: ACCEPTANCE-0001: Single Product Vertical Slice"}),
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
    assert result.resolved_model == "gpt-5.2-mini"
    model_resolution = json.loads((tmp_path / "runtime" / "local_execution" / "model_resolution.json").read_text(encoding="utf-8"))
    assert model_resolution["resolved_model"] == "gpt-5.2-mini"
    assert model_resolution["model_policy"] == "cost_optimized"
    assert model_resolution["candidate_models"][0] == "gpt-5.2-mini"
    assert model_resolution["fallback_used"] is False
    assert model_resolution["estimated_cost_tier"] == "lowest"
    assert "resolved_at" in model_resolution


def test_local_execution_model_resolution_falls_back_to_next_lowest(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({"request_id": "REQ-1", "request_status": "ready", "next_action": "Issue #28: ACCEPTANCE-0001: Single Product Vertical Slice"}),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Constitution v3 Freeze"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}), encoding="utf-8")
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._supported_models = lambda: ["gpt-5.4-mini", "gpt-5.4"]  # type: ignore[method-assign]
    result = adapter.run(dry_run=True)
    model_resolution = json.loads((tmp_path / "runtime" / "local_execution" / "model_resolution.json").read_text(encoding="utf-8"))
    assert model_resolution["resolved_model"] == "gpt-5.4-mini"
    assert model_resolution["candidate_models"] == ["gpt-5.4-mini", "gpt-5.4"]
    assert model_resolution["estimated_cost_tier"] == "low"
    assert model_resolution["selection_reason"].startswith("capability=")
    assert model_resolution["fallback_used"] is False
    assert result.resolved_model == "gpt-5.4-mini"


def test_local_execution_model_resolution_fail_closed_when_no_supported_model(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({"request_id": "REQ-1", "request_status": "ready", "next_action": "Issue #28: ACCEPTANCE-0001: Single Product Vertical Slice"}),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Constitution v3 Freeze"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}), encoding="utf-8")
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._supported_models = lambda: []  # type: ignore[method-assign]
    try:
        adapter.run(dry_run=True)
    except Exception as exc:
        assert "Model resolution failed" in str(exc)
    else:
        raise AssertionError("expected model resolution failure")
