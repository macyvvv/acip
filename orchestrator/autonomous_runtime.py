from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.execution_journal import ExecutionJournal
from orchestrator.execution_request import ExecutionRequestBuilder
from orchestrator.execution_session import ExecutionSessionManager
from orchestrator.execution_kernel import ExecutionKernel, ExecutionKernelResult
from orchestrator.repository_governor import RepositoryGovernor
from orchestrator.repository_state_manager import RepositoryStateManager
from orchestrator.worker_lifecycle import WorkerLifecycleManager


@dataclass(frozen=True)
class AutonomousRuntimeResult:
    repository_state: object
    governor_recommendation: object
    planning_cycle: object
    execution_request: object
    execution_session: object
    worker_lifecycle: object
    execution_journal_entry: object
    next_action: str


class AutonomousRuntime:
    def __init__(self, kernel: ExecutionKernel, base_path: str | Path = ".") -> None:
        self.kernel = kernel
        self.base_path = Path(base_path)

    def run(self) -> AutonomousRuntimeResult:
        repository_state = RepositoryStateManager(self.base_path).build_state([])
        governor = RepositoryGovernor(self.base_path)
        recommendation = governor.load_recommendation()
        planning_cycle = self.kernel.run_default_planning_cycle()
        candidate = recommendation.candidates[0] if recommendation.candidates else None
        request_builder = ExecutionRequestBuilder(self.base_path)
        execution_request = request_builder.from_governor_candidate(
            candidate.ep if candidate else "EP-0000",
            request_priority=candidate.priority if candidate else 0,
            approval_required=bool(candidate and candidate.human_approval_required),
            dependency=(),
            worker_assignment=planning_cycle.worker_assignment if planning_cycle.worker_assignment else None,
        )
        request_builder.write_runtime_request(execution_request)

        session_manager = ExecutionSessionManager(self.base_path)
        session = session_manager.start("SESSION-0001")
        session_manager.write_session(session)

        worker_state = self.kernel.load_worker_state()
        lifecycle_manager = WorkerLifecycleManager(self.base_path)
        lifecycle = lifecycle_manager.transition(worker_state, "Reserved")
        lifecycle_manager.validate_transition(lifecycle)
        lifecycle_manager.write_runtime_state(lifecycle)

        journal = ExecutionJournal(self.base_path)
        journal_entry = journal.new_entry(
            session_id=session.session_id,
            worker_name=worker_state.worker_name,
            request_id=execution_request.request_id,
            result="planned",
            review="pending",
        )
        journal.append(journal_entry)

        runtime_dir = self.base_path / "runtime" / "runtime_state"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "repository_state": {
                "queue_status": repository_state.queue_status,
                "active_ep": repository_state.active_ep,
                "next_ep": repository_state.next_ep,
            },
            "governor_recommendation_version": recommendation.version,
            "next_action": planning_cycle.next_action,
        }
        (runtime_dir / "runtime_state.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "RUNTIME_STATE.md").write_text(
            "\n".join(
                [
                    "# RUNTIME_STATE",
                    "",
                    f"next_action: {planning_cycle.next_action}",
                    f"execution_request: {execution_request.request_id}",
                    f"execution_session: {session.session_id}",
                    f"worker_state: {lifecycle.current_state}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return AutonomousRuntimeResult(
            repository_state=repository_state,
            governor_recommendation=recommendation,
            planning_cycle=planning_cycle,
            execution_request=execution_request,
            execution_session=session,
            worker_lifecycle=lifecycle,
            execution_journal_entry=journal_entry,
            next_action=planning_cycle.next_action,
        )
