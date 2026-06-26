from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.output_contract import CodexOutputContract, ValidationResult, WorktreeState, build_output_contract
from orchestrator.validation_orchestrator import ValidationOrchestrationResult


@dataclass(frozen=True)
class CompletionReport:
    output_contract: CodexOutputContract
    validation_status: str
    journal_status: str
    runtime_status: str
    next_action: str


class CompletionReportAutomationError(ValueError):
    pass


class CompletionReportAutomation:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def build(
        self,
        *,
        task_id: str,
        validation_result: ValidationOrchestrationResult,
        commit_sha: str | None,
        worktree_state: WorktreeState,
        next_action: str,
    ) -> CompletionReport:
        contract = build_output_contract(
            task_id=task_id,
            validation_results=[
                ValidationResult(command=step.command, exit_code=step.exit_code, output=step.output)
                for step in validation_result.validation_steps
            ]
            + (
                [ValidationResult(command=validation_result.pytest_result.command, exit_code=validation_result.pytest_result.exit_code, output=validation_result.pytest_result.output)]
                if validation_result.pytest_result is not None
                else []
            ),
            commit_sha=commit_sha,
            worktree_state=worktree_state,
            next_action=next_action,
            rerun_validation_conditions=list(validation_result.rerun_required_when),
        )
        return CompletionReport(
            output_contract=contract,
            validation_status="success" if validation_result.overall_success else "failure",
            journal_status="recorded",
            runtime_status="recorded",
            next_action=next_action,
        )

    def write(self, report: CompletionReport) -> None:
        runtime_dir = self.base_path / "runtime" / "completion"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "task_id": report.output_contract.task_id,
            "commit_sha": report.output_contract.commit_sha,
            "worktree_clean": report.output_contract.worktree_state.clean,
            "validation_status": report.validation_status,
            "next_action": report.next_action,
            "rerun_validation_conditions": report.output_contract.rerun_validation_conditions,
        }
        (runtime_dir / "completion_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "COMPLETION_REPORT.md").write_text(
            "\n".join(
                [
                    "# COMPLETION_REPORT",
                    "",
                    f"task_id: {report.output_contract.task_id}",
                    f"validation_status: {report.validation_status}",
                    f"next_action: {report.next_action}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

