from __future__ import annotations

import json
from pathlib import Path

from system.orchestrator.local_execution_adapter import LocalExecutionAdapter, LocalExecutionError


def _prepare_base(tmp_path: Path) -> None:
    (tmp_path / "runtime" / "request").mkdir(parents=True)
    (tmp_path / "runtime" / "request" / "execution_request.json").write_text(
        json.dumps(
            {
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
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "runtime" / "supervisor").mkdir(parents=True)
    (tmp_path / "runtime" / "supervisor" / "latest.json").write_text(json.dumps({"codex_intake_payload": {"current_ep": "EP-0201"}}), encoding="utf-8")
    (tmp_path / "runtime" / "planning").mkdir(parents=True)
    (tmp_path / "runtime" / "planning" / "latest.json").write_text(json.dumps({"current_objective": "Product Launch Checklist"}), encoding="utf-8")
    (tmp_path / "runtime" / "repository_state").mkdir(parents=True)
    (tmp_path / "runtime" / "repository_state" / "latest.json").write_text(
        json.dumps({"repository_health": "healthy", "validation_status": "success", "worktree_state": "clean", "approval_required": False}),
        encoding="utf-8",
    )
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


def test_first_model_fails_second_succeeds(tmp_path: Path) -> None:
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)
    calls: list[str] = []

    def fake_run(command: list[str]):
        model = command[3]
        calls.append(model)
        if model == "gpt-5.4-mini":
            return type("Result", (), {"stdout": "", "stderr": "capacity", "returncode": 1})()
        return type("Result", (), {"stdout": "ok", "stderr": "", "returncode": 0})()

    adapter._run_command = fake_run  # type: ignore[method-assign]
    result = adapter.run(dry_run=False, approval_flag=True)

    assert calls == ["gpt-5.4-mini", "gpt-5.4"]
    assert result.resolved_model == "gpt-5.4-mini"
    assert result.model_attempts == [
        {"model": "gpt-5.4-mini", "result": "capacity_fail"},
        {"model": "gpt-5.4", "result": "success"},
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
        assert "Codex command failed" in str(exc) or "blocked_by_usage_limit" in str(exc) or "missing_deliverables" in str(exc)
    else:
        raise AssertionError("LocalExecutionError not raised")


def test_attempts_are_logged(tmp_path: Path) -> None:
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)

    def fake_run(command: list[str]):
        model = command[3]
        if model == "gpt-5.4-mini":
            return type("Result", (), {"stdout": "", "stderr": "capacity", "returncode": 1})()
        return type("Result", (), {"stdout": "ok", "stderr": "", "returncode": 0})()

    adapter._run_command = fake_run  # type: ignore[method-assign]
    result = adapter.run(dry_run=False, approval_flag=True)
    payload = json.loads((tmp_path / "runtime" / "local_execution" / "latest.json").read_text(encoding="utf-8"))

    assert payload["model_attempts"] == result.model_attempts
    assert payload["model_attempts"][0]["result"] == "capacity_fail"


def test_chatgpt_auth_fallback_chain_excludes_unsupported_models(tmp_path: Path) -> None:
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._supported_models = lambda: ["gpt-5.4-mini", "gpt-5.3-mini", "gpt-5.4"]  # type: ignore[method-assign]
    adapter._auth_mode = lambda: "chatgpt"  # type: ignore[method-assign]
    chain = adapter._model_fallback_chain("gpt-5.4-mini")
    assert chain == ["gpt-5.4-mini", "gpt-5.4"]


def test_chatgpt_auth_skips_unsupported_fallback_attempts(tmp_path: Path) -> None:
    _prepare_base(tmp_path)
    adapter = LocalExecutionAdapter(tmp_path)
    adapter._supported_models = lambda: ["gpt-5.4-mini", "gpt-5.3-mini", "gpt-5.4"]  # type: ignore[method-assign]
    adapter._auth_mode = lambda: "chatgpt"  # type: ignore[method-assign]
    attempts: list[str] = []

    def fake_run(command: list[str]):
        model = command[3]
        attempts.append(model)
        if model == "gpt-5.4-mini":
            return type("Result", (), {"stdout": "", "stderr": "capacity", "returncode": 1})()
        return type("Result", (), {"stdout": "ok", "stderr": "", "returncode": 0})()

    adapter._run_command = fake_run  # type: ignore[method-assign]
    result = adapter.run(dry_run=False, approval_flag=True)

    assert attempts == ["gpt-5.4-mini", "gpt-5.4"]
    assert all(attempt["model"] != "gpt-5.3-mini" for attempt in result.model_attempts)
