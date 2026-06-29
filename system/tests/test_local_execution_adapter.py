from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.local_execution_adapter import LocalExecutionAdapter


def test_local_execution_adapter_dry_run(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({
            "request_id": "REQ-ACCEPTANCE-0001",
            "request_status": "ready",
            "request_priority": 100,
            "approval_required": False,
            "dependency": ["system/runtime/supervisor/latest.json"],
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
    assert result.codex_cli_command == 'codex exec -m gpt-5.4-mini "$(cat system/runtime/local_execution/codex_prompt.md)"'
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
    assert result.resolved_model == "gpt-5.4-mini"
    model_resolution = json.loads((tmp_path / "runtime" / "local_execution" / "model_resolution.json").read_text(encoding="utf-8"))
    assert model_resolution["auth_mode"] == "chatgpt"
    assert model_resolution["resolved_model"] == "gpt-5.4-mini"
    assert model_resolution["model_policy"] == "cost_optimized"
    assert model_resolution["candidate_models"][0] == "gpt-5.2-mini"
    assert model_resolution["supported_models"][0] == "gpt-5.4-mini"
    assert model_resolution["rejected_models"][0]["model"] == "gpt-5.2-mini"
    assert model_resolution["fallback_used"] is True
    assert model_resolution["estimated_cost_tier"] == "low"
    assert "resolved_at" in model_resolution
    prompt = (tmp_path / "runtime" / "local_execution" / "codex_prompt.md").read_text(encoding="utf-8")
    assert "Implement the selected work item using repository artifacts only." in prompt
    assert result.codex_cli_command == 'codex exec -m gpt-5.4-mini "$(cat system/runtime/local_execution/codex_prompt.md)"'


def test_local_execution_model_resolution_unsupported_model_never_emitted(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({"request_id": "REQ-1", "request_status": "ready", "next_action": "Issue #30: PRODUCT-0001: Product Launch Checklist", "issue_number": 30, "issue_title": "PRODUCT-0001: Product Launch Checklist"}),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Constitution v3 Freeze"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}), encoding="utf-8")
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._supported_models = lambda: ["gpt-5.2-mini"]  # type: ignore[method-assign]
    adapter._auth_mode = lambda: "chatgpt"  # type: ignore[method-assign]
    try:
        adapter.run(dry_run=True)
    except Exception as exc:
        latest = json.loads((tmp_path / "runtime" / "local_execution" / "latest.json").read_text(encoding="utf-8"))
        assert latest["failure_reason"] == "unsupported_model_for_auth_mode"
        assert latest["resolved_model"] is None
        assert latest["blocked_by_usage_limit"] is False
        assert "gpt-5.2-mini" not in latest["codex_cli_command"]
        assert "unsupported_model_for_auth_mode" in str(exc)
    else:
        raise AssertionError("expected auth-mode model failure")


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


def test_local_execution_prompt_uses_selected_issue(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({
            "request_id": "REQ-ISSUE-0030",
            "request_status": "ready",
            "request_priority": 100,
            "approval_required": False,
            "dependency": ["system/runtime/planning/latest.json"],
            "worker_assignment": "Codex",
            "next_action": "Issue #30: PRODUCT-0001: Product Launch Checklist",
            "objective": "Product Launch Checklist",
            "candidate_source": [],
            "issue_number": 30,
            "issue_title": "PRODUCT-0001: Product Launch Checklist",
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
    prompt = (tmp_path / "runtime" / "local_execution" / "codex_prompt.md").read_text(encoding="utf-8")
    assert "Implement Issue #30 / PRODUCT-0001: Product Launch Checklist" in prompt
    assert "Selected Issue Number: 30" in prompt
    assert "Selected Issue Title: PRODUCT-0001: Product Launch Checklist" in prompt
    assert "Constitution v3 Freeze" not in prompt
    assert result.blocked_by_usage_limit is False


def test_local_execution_usage_limit_is_recorded_as_blocked(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({
            "request_id": "REQ-ISSUE-0030",
            "request_status": "ready",
            "approval_required": False,
            "dependency": ["system/runtime/planning/latest.json"],
            "worker_assignment": "Codex",
            "next_action": "Issue #30: PRODUCT-0001: Product Launch Checklist",
            "objective": "Product Launch Checklist",
            "candidate_source": [],
            "issue_number": 30,
            "issue_title": "PRODUCT-0001: Product Launch Checklist",
        }),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Product Launch Checklist"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}), encoding="utf-8")
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._run_command = lambda command: type("Result", (), {"stdout": "", "stderr": "ERROR: You've hit your usage limit.", "returncode": 2})()  # type: ignore[method-assign]
    try:
        adapter.run(dry_run=False, approval_flag=True)
    except Exception:
        latest = json.loads((tmp_path / "runtime" / "local_execution" / "latest.json").read_text(encoding="utf-8"))
        assert latest["blocked_by_usage_limit"] is True
        assert "usage limit" in latest["stderr"].lower()
    else:
        raise AssertionError("expected usage-limit failure")


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
        assert "unsupported_model_for_auth_mode" in str(exc)
    else:
        raise AssertionError("expected model resolution failure")


def test_local_execution_missing_deliverables_sets_failure_reason(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({
            "request_id": "REQ-ISSUE-0030",
            "request_status": "ready",
            "next_action": "Issue #30: PRODUCT-0001: Product Launch Checklist",
            "issue_number": 30,
            "issue_title": "PRODUCT-0001: Product Launch Checklist",
            "objective": "Product Launch Checklist",
        }),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Product Launch Checklist"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}), encoding="utf-8")
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._run_command = lambda command: type("Result", (), {"stdout": "", "stderr": "", "returncode": 0})()  # type: ignore[method-assign]
    try:
        adapter.run(dry_run=False, approval_flag=True)
    except Exception:
        latest = json.loads((tmp_path / "runtime" / "local_execution" / "latest.json").read_text(encoding="utf-8"))
        assert latest["failure_reason"] == "missing_deliverables"
        assert latest["blocked_by_usage_limit"] is False
        assert latest["exit_code"] == 1
        failures = json.loads((tmp_path / "system" / "runtime" / "knowledge" / "failures.json").read_text(encoding="utf-8"))
        assert failures[-1]["issue_number"] == 30
        assert failures[-1]["error_type"] == "unknown"
    else:
        raise AssertionError("expected missing deliverables failure")


def test_local_execution_verifies_required_product_deliverables(tmp_path: Path) -> None:
    base = tmp_path / "product" / "minimal_launch_brief_generator"
    (base / "src").mkdir(parents=True)
    (base / "tests").mkdir(parents=True)
    for relative_path in [
        "README.md",
        "requirements.md",
        "architecture.md",
        "release_notes.md",
        "src/__init__.py",
        "src/minimal_launch_brief_generator.py",
        "tests/test_minimal_launch_brief_generator.py",
    ]:
        (base / relative_path).write_text("ok", encoding="utf-8")
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps({
            "request_id": "REQ-ISSUE-0030",
            "request_status": "ready",
            "next_action": "Issue #30: PRODUCT-0001: Product Launch Checklist",
            "issue_number": 30,
            "issue_title": "PRODUCT-0001: Product Launch Checklist",
            "objective": "Product Launch Checklist",
        }),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Product Launch Checklist"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}), encoding="utf-8")
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._run_command = lambda command: type("Result", (), {"stdout": "", "stderr": "", "returncode": 0})()  # type: ignore[method-assign]
    result = adapter.run(dry_run=False, approval_flag=True)
    assert result.failure_reason is None
