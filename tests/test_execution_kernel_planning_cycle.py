from __future__ import annotations

from orchestrator.dispatcher import Dispatcher
from orchestrator.execution_kernel import ExecutionKernel


def test_execution_kernel_runs_default_planning_cycle() -> None:
    kernel = ExecutionKernel(dispatcher=Dispatcher({}), base_path=".")
    result = kernel.run_default_planning_cycle()
    assert result.next_action
