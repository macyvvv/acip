from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from orchestrator.autonomous_loop import AutonomousExecutionSummary, run_autonomous_execution_loop
from orchestrator.capability_router import CapabilityRoute, CapabilityRouter
from orchestrator.context_loader import Context, load_context
from orchestrator.dispatcher import Dispatcher
from orchestrator.output_contract import CodexOutputContract
from orchestrator.planner import PlannerDecision, load_planner_decision
from orchestrator.queue_state import QueueState, read_queue_state
from orchestrator.validation_orchestrator import ValidationOrchestrationResult, ValidationOrchestrator
from orchestrator.worker_state import WorkerState, read_worker_state
from workers.registry import WorkerRegistry, load_worker_registry


@dataclass(frozen=True)
class ExecutionKernelResult:
    success: bool
    next_action: str | None
    error: str | None = None
    planner: PlannerDecision | None = None
    queue_state: QueueState | None = None
    worker_state: WorkerState | None = None
    worker_assignment: str | None = None
    autonomous_loop: AutonomousExecutionSummary | None = None
    validation_result: ValidationOrchestrationResult | None = None
    output_contract: CodexOutputContract | None = None
    worker_registry: WorkerRegistry | None = None
    capability_route: CapabilityRoute | None = None


class ExecutionKernelError(RuntimeError):
    pass


@dataclass
class ExecutionKernel:
    dispatcher: Dispatcher
    base_path: str | Path = "."

    def _root(self) -> Path:
        return Path(self.base_path)

    def load_context(self) -> Context:
        return load_context(self._root())

    def load_worker_registry(self) -> WorkerRegistry:
        return load_worker_registry(self._root() / "workers" / "registry.yaml")

    def load_queue_state(self) -> QueueState:
        return read_queue_state(self._root() / "docs" / "current" / "QUEUE_STATE.md")

    def load_worker_state(self) -> WorkerState:
        return read_worker_state(self._root() / "docs" / "current" / "WORKER_STATE.md")

    def plan(self) -> PlannerDecision:
        return load_planner_decision(self._root())

    def worker_assignment(self) -> str:
        route = self.route_worker()
        return route.worker_name

    def route_worker(self) -> CapabilityRoute:
        planner = self.plan()
        router = CapabilityRouter(self._root())
        return router.route(
            planner,
            required_capabilities=("repository_implementation", "validation_execution"),
            prohibited_actions=("approve", "deploy"),
            required_validation_responsibility=("run_repository_validation",),
            execution_boundary=("push_directly_to_main",),
        )

    def run_validation(self) -> ValidationOrchestrationResult:
        orchestrator = ValidationOrchestrator(self._root())
        result = orchestrator.run()
        orchestrator.write_reports(result)
        return result

    def run_autonomous_cycle(self) -> ExecutionKernelResult:
        try:
            worker_registry = self.load_worker_registry()
            capability_route = self.route_worker()
            loop = run_autonomous_execution_loop(self.dispatcher, self._root())
            return ExecutionKernelResult(
                success=True,
                next_action=loop.output_contract.next_action,
                planner=loop.planner,
                queue_state=loop.queue_state,
                worker_state=loop.worker_state,
                worker_assignment=capability_route.worker_name,
                autonomous_loop=loop,
                output_contract=loop.output_contract,
                worker_registry=worker_registry,
                capability_route=capability_route,
            )
        except Exception as exc:  # pragma: no cover - kernel boundary
            return ExecutionKernelResult(success=False, next_action=None, error=str(exc))

    def run_validation_pipeline(self) -> ExecutionKernelResult:
        try:
            result = self.run_validation()
            return ExecutionKernelResult(
                success=result.overall_success,
                next_action="python scripts/validate_all.py",
                validation_result=result,
                worker_registry=self.load_worker_registry(),
                capability_route=self.route_worker(),
            )
        except Exception as exc:  # pragma: no cover - kernel boundary
            return ExecutionKernelResult(success=False, next_action=None, error=str(exc))
