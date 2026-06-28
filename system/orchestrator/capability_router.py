from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from system.orchestrator.planner import PlannerDecision
from workers.capability_matcher import CapabilityMatch, score_worker
from workers.registry import WorkerRegistry, WorkerRegistryError, load_worker_registry


@dataclass(frozen=True)
class CapabilityRoute:
    worker_name: str
    reason: str
    candidates: tuple[str, ...]


class CapabilityRouterError(ValueError):
    pass


class CapabilityRouter:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def load_registry(self) -> WorkerRegistry:
        return load_worker_registry(self.base_path / "workers" / "registry.yaml")

    def route(
        self,
        planner: PlannerDecision,
        required_capabilities: tuple[str, ...],
        prohibited_actions: tuple[str, ...] = (),
        required_validation_responsibility: tuple[str, ...] = (),
        execution_boundary: tuple[str, ...] = (),
    ) -> CapabilityRoute:
        registry = self.load_registry()
        matches: list[CapabilityMatch] = []
        for worker in registry.workers.values():
            match = score_worker(
                worker,
                required_capabilities=required_capabilities,
                prohibited_actions=prohibited_actions,
                required_validation_responsibility=required_validation_responsibility,
                execution_boundary=execution_boundary,
            )
            if match is not None:
                matches.append(match)
        if not matches:
            raise CapabilityRouterError(
                f"No worker matches capabilities for EP {planner.next_ep}"
            )
        matches.sort(key=lambda item: item.score, reverse=True)
        top = matches[0]
        candidate_names = tuple(match.worker_name for match in matches)
        return CapabilityRoute(
            worker_name=top.worker_name,
            reason=f"Selected by capability score for {planner.next_ep}",
            candidates=candidate_names,
        )
