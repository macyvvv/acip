from __future__ import annotations

from dataclasses import dataclass

from workers.registry import WorkerRegistryEntry


@dataclass(frozen=True)
class CapabilityMatch:
    worker_name: str
    score: tuple[int, int, int, int, str]


def score_worker(
    worker: WorkerRegistryEntry,
    required_capabilities: tuple[str, ...],
    prohibited_actions: tuple[str, ...],
    required_validation_responsibility: tuple[str, ...],
    execution_boundary: tuple[str, ...],
) -> CapabilityMatch | None:
    capability_hits = len(set(required_capabilities) & set(worker.capability))
    validation_hits = len(set(required_validation_responsibility) & set(worker.validation_responsibility))
    if capability_hits == 0:
        return None
    if set(prohibited_actions) & set(worker.allowed_actions):
        return None
    if set(execution_boundary) & set(worker.allowed_actions):
        return None
    if required_validation_responsibility and validation_hits == 0:
        return None
    return CapabilityMatch(
        worker_name=worker.name,
        score=(
            capability_hits,
            validation_hits,
            len(worker.allowed_actions),
            -len(worker.prohibited_actions),
            worker.name,
        ),
    )
