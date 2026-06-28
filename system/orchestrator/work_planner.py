from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class WorkCandidate:
    candidate_id: str
    title: str
    proposed_pack_or_ep: str
    objective: str
    rationale: str
    mission_contribution: int
    management_cost_reduction: int
    risk_reduction: int
    strategic_value: int
    operational_value: int
    learning_value: int
    dependencies: list[str]
    blocked_by: list[str]
    approval_required: bool
    recommended_action: str
    issue_body_draft: str


@dataclass(frozen=True)
class WorkPlan:
    generated_at: str
    mission_alignment: str
    current_phase: str
    current_objective: str
    candidate_items: list[WorkCandidate]
    parking_lot: list[str]
    blocked_candidates: list[str]
    source_artifacts: list[str]


class WorkPlanner:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def _path(self, *parts: str) -> Path:
        system_path = self.base_path / "system" / Path(*parts)
        legacy_path = self.base_path / Path(*parts)
        return system_path if system_path.exists() or not legacy_path.exists() else legacy_path

    def build(self) -> WorkPlan:
        planning = self._read_json(self._path("runtime", "planning", "latest.json"))
        repository = self._read_json(self._path("runtime", "repository_state", "latest.json"))
        constitution = self._read_json(self._path("runtime", "repository_constitution", "constitution.json"))
        current_phase = planning.get("current_phase", "unknown")
        current_objective = planning.get("current_objective", "unknown")
        candidates = [self._candidate(payload) for payload in self._candidate_payloads()]
        parking_lot = ["current queue items beyond the active planning horizon"]
        blocked_candidates = ["EP-0199 requires approval gate review"] if repository.get("approval_required") else []
        source_artifacts = [
            "system/runtime/planning/latest.json",
            "system/runtime/repository_state/latest.json",
            "system/runtime/repository_constitution/constitution.json",
            "queue/",
            "packs/",
            "system/runtime/handoff/latest.json",
            "system/runtime/event_runtime/",
            "system/runtime/root_hygiene/",
        ]
        if constitution.get("status"):
            current_phase = planning.get("current_phase", current_phase)
        return WorkPlan(
            generated_at="deterministic",
            mission_alignment=planning.get("mission", "unknown"),
            current_phase=current_phase,
            current_objective=current_objective,
            candidate_items=candidates,
            parking_lot=parking_lot,
            blocked_candidates=blocked_candidates,
            source_artifacts=source_artifacts,
        )

    def write(self, plan: WorkPlan) -> None:
        payload = asdict(plan)
        for runtime_dir in (self.base_path / "system" / "runtime" / "work_planner", self.base_path / "runtime" / "work_planner"):
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (runtime_dir / "latest.md").write_text(self._to_markdown(plan), encoding="utf-8")

    def _to_markdown(self, plan: WorkPlan) -> str:
        return "\n".join([
            "# WORK_PLANNER",
            "",
            f"generated_at: {plan.generated_at}",
            f"mission_alignment: {plan.mission_alignment}",
            f"current_phase: {plan.current_phase}",
            f"current_objective: {plan.current_objective}",
            f"candidate_count: {len(plan.candidate_items)}",
            "",
        ])

    def _candidate_payloads(self) -> list[dict[str, object]]:
        return [
            {"candidate_id": "WP-0194", "title": "EP-0194 Work Planner Contract", "proposed_pack_or_ep": "EP-0194", "objective": "Define the work planner contract.", "rationale": "Establish the projection boundary before scoring and rendering.", "mission_contribution": 5, "management_cost_reduction": 5, "risk_reduction": 4, "strategic_value": 5, "operational_value": 5, "learning_value": 3, "dependencies": ["PACK-0012"], "blocked_by": [], "approval_required": False, "recommended_action": "create_issue", "issue_body_draft": "Implement EP-0194 Work Planner Contract as a deterministic projection layer."},
            {"candidate_id": "WP-0195", "title": "EP-0195 Candidate Source Aggregator", "proposed_pack_or_ep": "EP-0195", "objective": "Aggregate candidate sources.", "rationale": "Collect deterministic inputs before ranking.", "mission_contribution": 5, "management_cost_reduction": 5, "risk_reduction": 4, "strategic_value": 4, "operational_value": 5, "learning_value": 3, "dependencies": ["EP-0194"], "blocked_by": [], "approval_required": False, "recommended_action": "create_issue", "issue_body_draft": "Implement EP-0195 Candidate Source Aggregator with deterministic source collection."},
            {"candidate_id": "WP-0196", "title": "EP-0196 Work Candidate Scoring Model", "proposed_pack_or_ep": "EP-0196", "objective": "Score work candidates deterministically.", "rationale": "Prioritize work using stable criteria.", "mission_contribution": 5, "management_cost_reduction": 4, "risk_reduction": 4, "strategic_value": 5, "operational_value": 5, "learning_value": 4, "dependencies": ["EP-0195"], "blocked_by": [], "approval_required": False, "recommended_action": "create_issue", "issue_body_draft": "Implement EP-0196 Work Candidate Scoring Model with deterministic ranking."},
            {"candidate_id": "WP-0197", "title": "EP-0197 Issue Candidate Renderer", "proposed_pack_or_ep": "EP-0197", "objective": "Render issue bodies for candidates.", "rationale": "Convert recommendations into reviewable issue drafts.", "mission_contribution": 4, "management_cost_reduction": 4, "risk_reduction": 3, "strategic_value": 4, "operational_value": 5, "learning_value": 4, "dependencies": ["EP-0196"], "blocked_by": [], "approval_required": False, "recommended_action": "create_issue", "issue_body_draft": "Implement EP-0197 Issue Candidate Renderer for repository-native issue drafts."},
            {"candidate_id": "WP-0198", "title": "EP-0198 Parking Lot and Blocked Candidate Handling", "proposed_pack_or_ep": "EP-0198", "objective": "Separate blocked and deferred candidates.", "rationale": "Prevent high-risk or out-of-scope work from entering active planning.", "mission_contribution": 4, "management_cost_reduction": 5, "risk_reduction": 5, "strategic_value": 4, "operational_value": 4, "learning_value": 3, "dependencies": ["EP-0196"], "blocked_by": [], "approval_required": False, "recommended_action": "create_issue", "issue_body_draft": "Implement EP-0198 Parking Lot and Blocked Candidate Handling."},
            {"candidate_id": "WP-0199", "title": "EP-0199 Work Planner Review Gate", "proposed_pack_or_ep": "EP-0199", "objective": "Add review gate for planner output.", "rationale": "Ensure recommendations are reviewable before action.", "mission_contribution": 4, "management_cost_reduction": 4, "risk_reduction": 5, "strategic_value": 4, "operational_value": 4, "learning_value": 3, "dependencies": ["EP-0197", "EP-0198"], "blocked_by": [], "approval_required": True, "recommended_action": "review", "issue_body_draft": "Implement EP-0199 Work Planner Review Gate with approval requirements."},
            {"candidate_id": "WP-0200", "title": "EP-0200 Work Planner Validation", "proposed_pack_or_ep": "EP-0200", "objective": "Validate the work planner outputs.", "rationale": "Close the loop with deterministic validation.", "mission_contribution": 5, "management_cost_reduction": 5, "risk_reduction": 5, "strategic_value": 5, "operational_value": 5, "learning_value": 4, "dependencies": ["EP-0199"], "blocked_by": [], "approval_required": False, "recommended_action": "create_issue", "issue_body_draft": "Implement EP-0200 Work Planner Validation for deterministic output checks."},
        ]

    def _candidate(self, payload: dict[str, object]) -> WorkCandidate:
        return WorkCandidate(**payload)

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
