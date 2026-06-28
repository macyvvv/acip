from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json

from system.orchestrator.capability_router import CapabilityRouter
from system.orchestrator.context_loader import load_context
from system.orchestrator.queue_state import read_queue_state
from workers.registry import load_worker_registry


@dataclass(frozen=True)
class GovernorCandidate:
    ep: str
    priority: int
    reason: str
    required_capability: str
    risk_level: str
    human_approval_required: bool


@dataclass(frozen=True)
class GovernorState:
    source_state: str
    active_ep: str
    next_ep: str
    candidates: tuple[GovernorCandidate, ...] = ()
    validation_status: str = "unknown"


@dataclass(frozen=True)
class GovernorRecommendation:
    version: int
    state: GovernorState
    candidates: tuple[GovernorCandidate, ...] = ()


class RepositoryGovernorError(RuntimeError):
    pass


class RepositoryGovernor:
    RECOMMENDATION_VERSION = 1

    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def build_candidates(self) -> tuple[GovernorCandidate, ...]:
        queue_state = read_queue_state(self.base_path / "docs" / "current" / "QUEUE_STATE.md")
        _ = load_worker_registry(self.base_path / "workers" / "registry.yaml")
        _ = CapabilityRouter(self.base_path)
        _ = load_context(self.base_path)

        candidates = [
            GovernorCandidate(
                ep=queue_state.next_ep,
                priority=100,
                reason="Continue the repository-defined EP sequence from the current queue state.",
                required_capability="repository_implementation",
                risk_level="low",
                human_approval_required=False,
            ),
            GovernorCandidate(
                ep="EP-0121",
                priority=80,
                reason="Repository layout remains report-only and can be promoted later.",
                required_capability="repository_governance",
                risk_level="medium",
                human_approval_required=False,
            ),
            GovernorCandidate(
                ep="EP-0117",
                priority=70,
                reason="Refactoring governance remains relevant for migrations but is not a destructive action.",
                required_capability="refactoring_governance",
                risk_level="medium",
                human_approval_required=False,
            ),
            GovernorCandidate(
                ep="EP-0123",
                priority=60,
                reason="Layout enforcement can follow the canonicalization groundwork, but it is high risk because it changes repository-wide enforcement.",
                required_capability="repository_governance",
                risk_level="high",
                human_approval_required=True,
            ),
        ]
        return tuple(sorted(candidates, key=lambda item: (-item.priority, item.ep)))

    def recommend(self) -> GovernorRecommendation:
        candidates = self.build_candidates()
        queue_state = read_queue_state(self.base_path / "docs" / "current" / "QUEUE_STATE.md")
        state = GovernorState(
            source_state="docs/current/STATE.md",
            active_ep=queue_state.active_ep,
            next_ep=queue_state.next_ep,
            candidates=candidates,
            validation_status=self._validation_status(),
        )
        return GovernorRecommendation(version=self.RECOMMENDATION_VERSION, state=state, candidates=candidates)

    def load_recommendation(self) -> GovernorRecommendation:
        path = self.base_path / "runtime" / "governor" / "governor_recommendations.json"
        if not path.exists():
            return self.recommend()
        payload = json.loads(path.read_text(encoding="utf-8"))
        state_payload = payload.get("state", {})
        candidates = tuple(
            GovernorCandidate(
                ep=item["ep"],
                priority=item["priority"],
                reason=item["reason"],
                required_capability=item["required_capability"],
                risk_level=item["risk_level"],
                human_approval_required=item["human_approval_required"],
            )
            for item in payload.get("candidates", [])
        )
        state = GovernorState(
            source_state=state_payload.get("source_state", "docs/current/STATE.md"),
            active_ep=state_payload.get("active_ep", "unknown"),
            next_ep=state_payload.get("next_ep", "unknown"),
            candidates=candidates,
            validation_status=state_payload.get("validation_status", "unknown"),
        )
        return GovernorRecommendation(version=payload.get("version", self.RECOMMENDATION_VERSION), state=state, candidates=candidates)

    def write_artifacts(self, recommendation: GovernorRecommendation) -> None:
        runtime_dir = self.base_path / "runtime" / "governor"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": recommendation.version,
            "state": {
                "source_state": recommendation.state.source_state,
                "active_ep": recommendation.state.active_ep,
                "next_ep": recommendation.state.next_ep,
                "validation_status": recommendation.state.validation_status,
            },
            "candidates": [
                {
                    "ep": candidate.ep,
                    "priority": candidate.priority,
                    "reason": candidate.reason,
                    "required_capability": candidate.required_capability,
                    "risk_level": candidate.risk_level,
                    "human_approval_required": candidate.human_approval_required,
                }
                for candidate in recommendation.candidates
            ],
        }
        (runtime_dir / "governor_recommendations.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        markdown_lines = ["# GOVERNOR_RECOMMENDATIONS", ""]
        for candidate in recommendation.candidates:
            markdown_lines.append(
                f"- {candidate.ep} | priority={candidate.priority} | risk={candidate.risk_level} | human_approval_required={str(candidate.human_approval_required).lower()}"
            )
        (runtime_dir / "GOVERNOR_RECOMMENDATIONS.md").write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")

        docs_current = self.base_path / "docs" / "current" / "GOVERNOR_STATE.md"
        docs_current.write_text(
            "\n".join(
                [
                    "# GOVERNOR_STATE",
                    "",
                    f"active_ep: {recommendation.state.active_ep}",
                    f"next_ep: {recommendation.state.next_ep}",
                    f"validation_status: {recommendation.state.validation_status}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _validation_status(self) -> str:
        validation_state = self.base_path / "docs" / "current" / "VALIDATION_STATE.md"
        if not validation_state.exists():
            return "unknown"
        for line in validation_state.read_text(encoding="utf-8").splitlines():
            if line.startswith("last_validation_status:"):
                return line.split(":", 1)[1].strip()
        return "unknown"
