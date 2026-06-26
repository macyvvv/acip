from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from orchestrator.autonomous_queue_runtime import AutonomousQueueRuntime
from orchestrator.codex_intake import CodexIntake
from orchestrator.completion_report_automation import CompletionReportAutomation
from orchestrator.next_work_resolver import NextWorkResolver
from orchestrator.output_contract import WorktreeState
from orchestrator.validation_orchestrator import ValidationOrchestrationResult, ValidationStepResult


@dataclass(frozen=True)
class HumanRemovalValidationResult:
    queue_readable: bool
    intake_resolved: bool
    runtime_resolved: bool
    completion_resolved: bool
    next_work_resolved: bool


class HumanRemovalValidation:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self) -> HumanRemovalValidationResult:
        intake = CodexIntake(self.base_path)
        payload = intake.read_next_handoff()
        request = intake.to_execution_request(payload)

        queue_resolved = bool(payload.pack_id)
        intake_resolved = bool(request.request_id)

        validation = ValidationOrchestrationResult(
            validation_steps=[ValidationStepResult(command="python3 scripts/validate_all.py", exit_code=0, success=True)],
            pytest_result=ValidationStepResult(command="python3 -m pytest -q", exit_code=0, success=True),
            overall_success=True,
        )
        completion = CompletionReportAutomation(self.base_path).build(
            task_id=request.request_id,
            validation_result=validation,
            commit_sha=None,
            worktree_state=WorktreeState(clean=True, changed_files=[]),
            next_action="Proceed to next repository item.",
        )
        runtime_result = AutonomousQueueRuntime(self.base_path).run()
        next_work = NextWorkResolver(self.base_path).resolve()
        return HumanRemovalValidationResult(
            queue_readable=queue_resolved,
            intake_resolved=intake_resolved,
            runtime_resolved=runtime_result.next_action == "Proceed to next repository item.",
            completion_resolved=completion.validation_status == "success",
            next_work_resolved=bool(next_work.selected.pack_id),
        )

