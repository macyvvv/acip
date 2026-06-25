from __future__ import annotations

from orchestrator.autonomous_runtime import AutonomousRuntime
from orchestrator.dispatcher import Dispatcher
from orchestrator.execution_kernel import ExecutionKernel


def test_autonomous_runtime_runs_and_returns_next_action() -> None:
    runtime = AutonomousRuntime(ExecutionKernel(dispatcher=Dispatcher({})), ".")
    result = runtime.run()
    assert result.next_action
