from __future__ import annotations

from dataclasses import dataclass, field

from system.orchestrator.task import Task


@dataclass(frozen=True)
class Result:
    artifacts: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    checkpoint_candidate: str | None = None
    current_state_candidate: str | None = None
    review_notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    next_task: Task | None = None
