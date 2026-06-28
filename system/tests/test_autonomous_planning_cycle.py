from __future__ import annotations

from system.orchestrator.autonomous_planning_cycle import AutonomousPlanningCycle
from system.orchestrator.execution_kernel import ExecutionKernel
from system.orchestrator.dispatcher import Dispatcher


def test_autonomous_planning_cycle_produces_next_action() -> None:
    cycle = AutonomousPlanningCycle(ExecutionKernel(dispatcher=Dispatcher({})), ".")
    result = cycle.run()
    assert result.next_action
