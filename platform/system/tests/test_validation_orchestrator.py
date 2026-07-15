from pathlib import Path

from system.orchestrator.validation_orchestrator import ValidationOrchestrator, ValidationOrchestrationResult, ValidationStepResult


def _write_validation_scripts(root: Path) -> None:
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "validate_ep_0100.py").write_text("print('ok')", encoding="utf-8")
    (scripts / "validate_ep_0111.py").write_text("print('ok')", encoding="utf-8")


def test_discover_validation_scripts_sorted(tmp_path: Path) -> None:
    _write_validation_scripts(tmp_path)
    orchestrator = ValidationOrchestrator(tmp_path)

    names = [path.name for path in orchestrator.discover_validation_scripts()]

    assert names == ["validate_ep_0100.py", "validate_ep_0111.py"]


def test_build_and_write_reports(tmp_path: Path) -> None:
    orchestrator = ValidationOrchestrator(tmp_path)
    result = ValidationOrchestrationResult(
        validation_steps=[
            ValidationStepResult(command="python platform/system/platform/scripts/validate_ep_0100.py", exit_code=0, success=True),
        ],
        pytest_result=ValidationStepResult(command="python -m pytest -q", exit_code=0, success=True),
        overall_success=True,
    )

    json_report, markdown_report = orchestrator.build_report(result)
    orchestrator.write_reports(result)

    assert '"overall_success": true' in json_report
    assert '"validation_owner": "Codex"' in json_report
    assert "# VALIDATION REPORT" in markdown_report
    assert (tmp_path / "runtime" / "validation" / "validation_report.json").exists()
    assert (tmp_path / "runtime" / "validation" / "VALIDATION_REPORT.md").exists()
    assert (tmp_path / "docs" / "current" / "VALIDATION_STATE.md").exists()
    state_text = (tmp_path / "docs" / "current" / "VALIDATION_STATE.md").read_text(encoding="utf-8")
    assert "last_validation_status: success" in state_text
    assert "validation_owner: Codex" in state_text
