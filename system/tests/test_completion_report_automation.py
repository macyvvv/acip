from __future__ import annotations

from orchestrator.completion_report_automation import CompletionReportAutomation
from orchestrator.output_contract import WorktreeState
from orchestrator.validation_orchestrator import ValidationOrchestrationResult, ValidationStepResult


def test_completion_report_automation_builds_report() -> None:
    automation = CompletionReportAutomation(".")
    validation = ValidationOrchestrationResult(
        validation_steps=[ValidationStepResult(command="python scripts/validate_all.py", exit_code=0, success=True)],
        pytest_result=ValidationStepResult(command="python -m pytest -q", exit_code=0, success=True),
        overall_success=True,
    )
    report = automation.build(
        task_id="EP-0147",
        validation_result=validation,
        commit_sha="abc123",
        worktree_state=WorktreeState(clean=True, changed_files=[]),
        next_action="Proceed to next repository item.",
    )
    assert report.validation_status == "success"
    assert report.output_contract.commit_sha == "abc123"
