from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    id: str
    artifact: str
    owner: str
    instruction: str
    done_conditions: str
    target_paths: tuple[str, ...] = ()


class TaskValidationError(ValueError):
    pass
