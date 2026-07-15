from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.local_execution_adapter import LocalExecutionAdapter, LocalExecutionError


def _prepare_base(tmp_path: Path, *, next_action: str = "Architecture change: high-risk restructure for Issue #30") -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps(
            {
                "request_id": "REQ-ISSUE-0030",
                "request_status": "ready",
                "request_priority": 100,
                "approval_required": False,
                "dependency": ["platform/system/runtime/planning/latest.json"],
                "worker_assignment": "Claude",
                "next_action": next_action,
                "objective": "Product Launch Checklist",
                "candidate_source": [],
                "issue_number": 30,
                "issue_title": "PRODUCT-0001: Product Launch Checklist",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Product Launch Checklist"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(
        json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}),
        encoding="utf-8",
    )
    base = tmp_path / "app" / "products" / "minimal_launch_brief_generator"
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


def _model_of(command: list[str]) -> str:
    # command shape: ["claude", "-p", <prompt>, "--model", <model>]
    return command[command.index("--model") + 1]


def test_first_model_fails_second_succeeds(tmp_path: Path) -> None:
    # high-risk work resolves to opus, then falls back to sonnet on capacity pressure.
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)
    calls: list[str] = []

    def fake_run(command: list[str]):
        model = _model_of(command)
        calls.append(model)
        if model == "claude-opus-4-8":
            return type("Result", (), {"stdout": "", "stderr": "capacity", "returncode": 1})()
        return type("Result", (), {"stdout": "ok", "stderr": "", "returncode": 0})()

    adapter._run_command = fake_run  # type: ignore[method-assign]
    result = adapter.run(dry_run=False, approval_flag=True)

    assert calls == ["claude-opus-4-8", "claude-sonnet-5"]
    assert result.resolved_model == "claude-opus-4-8"
    assert result.model_attempts == [
        {"model": "claude-opus-4-8", "result": "capacity_fail"},
        {"model": "claude-sonnet-5", "result": "success"},
    ]


def test_all_models_fail_raises(tmp_path: Path) -> None:
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)

    def fake_run(command: list[str]):
        return type("Result", (), {"stdout": "", "stderr": "capacity", "returncode": 1})()

    adapter._run_command = fake_run  # type: ignore[method-assign]
    try:
        adapter.run(dry_run=False, approval_flag=True)
    except LocalExecutionError as exc:
        assert "Claude command failed" in str(exc) or "blocked_by_usage_limit" in str(exc) or "missing_deliverables" in str(exc)
    else:
        raise AssertionError("LocalExecutionError not raised")


def test_attempts_are_logged(tmp_path: Path) -> None:
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)

    def fake_run(command: list[str]):
        model = _model_of(command)
        if model == "claude-opus-4-8":
            return type("Result", (), {"stdout": "", "stderr": "capacity", "returncode": 1})()
        return type("Result", (), {"stdout": "ok", "stderr": "", "returncode": 0})()

    adapter._run_command = fake_run  # type: ignore[method-assign]
    result = adapter.run(dry_run=False, approval_flag=True)
    payload = json.loads((tmp_path / "runtime" / "local_execution" / "latest.json").read_text(encoding="utf-8"))

    assert payload["model_attempts"] == result.model_attempts
    assert payload["model_attempts"][0]["result"] == "capacity_fail"


def test_fallback_chain_from_strongest_descends_by_cost(tmp_path: Path) -> None:
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)
    chain = adapter._model_fallback_chain("claude-opus-4-8")
    assert chain == ["claude-opus-4-8", "claude-sonnet-5", "claude-haiku-4-5"]
