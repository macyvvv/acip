from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from system.core.agent_state_manager import load_agent_state
from system.core.agent_turn_runner import AgentTurnResult, AgentTurnRunner, run_agent_turn


@dataclass(frozen=True)
class AgentThreadResult:
    thread_id: str | None
    turns_run: int
    final_state: str
    stop_reason: str
    turn_results: tuple[AgentTurnResult, ...] = field(default_factory=tuple)


class AgentThreadRunnerError(ValueError):
    pass


class AgentThreadRunner:
    def __init__(self, base_path: str | Path = ".", *, max_turns: int = 5) -> None:
        self.base_path = Path(base_path)
        self.max_turns = max_turns

    def run_thread(self) -> AgentThreadResult:
        if self.max_turns <= 0:
            raise AgentThreadRunnerError("max_turns must be positive")

        turn_results: list[AgentTurnResult] = []
        current_state = load_agent_state(self.base_path)
        thread_id = current_state.thread_id

        stop_reason = "max_turns_reached"
        for _ in range(self.max_turns):
            turn_result = run_agent_turn(self.base_path)
            turn_results.append(turn_result)
            current_state = load_agent_state(self.base_path)
            thread_id = thread_id or current_state.thread_id
            if current_state.state in {"completed", "blocked", "terminated"}:
                stop_reason = current_state.state
                break
            if turn_result.processed_message_id is None:
                stop_reason = "idle"
                break
        else:
            stop_reason = "max_turns_reached"

        return AgentThreadResult(
            thread_id=thread_id,
            turns_run=len(turn_results),
            final_state=current_state.state,
            stop_reason=stop_reason,
            turn_results=tuple(turn_results),
        )


def run_agent_thread(base_path: str | Path = ".", *, max_turns: int = 5) -> AgentThreadResult:
    return AgentThreadRunner(base_path, max_turns=max_turns).run_thread()
