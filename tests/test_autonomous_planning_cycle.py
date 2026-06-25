from __future__ import annotations

from orchestrator.autonomous_planning_cycle import AutonomousPlanningCycle
from orchestrator.execution_kernel import ExecutionKernel
from orchestrator.dispatcher import Dispatcher


def test_autonomous_planning_cycle_produces_next_action() -> None:
    cycle = AutonomousPlanningCycle(ExecutionKernel(dispatcher=Dispatcher({})), ".")
    result = cycle.run()
    assert result.next_action
