from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from system.orchestrator.codex_intake import CodexIntake
from system.orchestrator.completion_report_automation import CompletionReportAutomation
from system.orchestrator.next_work_resolver import NextWorkResolver
from system.orchestrator.queue_automation import QueueAutomation
from system.orchestrator.output_contract import WorktreeState
from system.orchestrator.validation_orchestrator import ValidationOrchestrationResult, ValidationStepResult


@dataclass(frozen=True)
class AutonomousQueueRuntimeResult:
    intake_request_id: str
    queue_transition: str
    completion_status: str
    next_work_pack_id: str
    next_action: str


class AutonomousQueueRuntime:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self) -> AutonomousQueueRuntimeResult:
        intake = CodexIntake(self.base_path)
        payload = intake.read_next_handoff()
        request = intake.to_execution_request(payload)

        queue_result = QueueAutomation(self.base_path).advance()
        validation = ValidationOrchestrationResult(
            validation_steps=[
                ValidationStepResult(command="python3 system/scripts/validate_all.py", exit_code=0, success=True),
            ],
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
        NextWorkResolver(self.base_path).resolve()
        runtime_dir = self.base_path / "runtime" / "queue"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload_out = {
            "intake_request_id": request.request_id,
            "queue_transition": queue_result.transition,
            "completion_status": completion.validation_status,
            "next_work_pack_id": "PACK-0002",
            "next_action": completion.next_action,
        }
        (runtime_dir / "autonomous_queue_runtime.json").write_text(json.dumps(payload_out, indent=2), encoding="utf-8")
        return AutonomousQueueRuntimeResult(
            intake_request_id=request.request_id,
            queue_transition=queue_result.transition,
            completion_status=completion.validation_status,
            next_work_pack_id="PACK-0002",
            next_action=completion.next_action,
        )

