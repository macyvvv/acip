from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass(frozen=True)
class PlanningStateProjection:
    mission: str
    long_term_goal: str
    current_phase: str
    current_objective: str
    current_scope: str
    current_pack: str
    current_ep: str
    wbs: list[str]
    approved_next_action: str
    parking_lot: list[str]
    refactoring_priorities: list[str]
    blocked_items: list[str]
    approval_required: bool
    source_artifacts: list[str]


class PlanningStateBuilder:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def build(self) -> PlanningStateProjection:
        project = self._parse_key_values(self.base_path / "docs" / "current" / "PROJECT.md")
        state = self._parse_state(self.base_path / "docs" / "current" / "STATE.md")
        roadmap = self._parse_roadmap(self.base_path / "docs" / "current" / "ROADMAP.md")
        repo_state = self._read_json(self.base_path / "runtime" / "repository_state" / "latest.json")
        constitution = self._read_json(self.base_path / "runtime" / "repository_constitution" / "constitution.json")
        validation = self._read_json(self.base_path / "runtime" / "validation" / "validation_report.json")
        packs = self._read_pack_ids()
        current_pack = repo_state.get("active_pack", packs[0] if packs else "unknown")
        current_ep = repo_state.get("active_ep", state.get("active_ep", state.get("next_action", "unknown")))
        blocked_items = self._blocked_items(repo_state, validation)
        parking_lot = self._parking_lot(repo_state, packs)
        refactoring_priorities = self._refactoring_priorities(repo_state, constitution)
        source_artifacts = [
            "docs/current/PROJECT.md",
            "docs/current/STATE.md",
            "docs/current/ROADMAP.md",
            "docs/current/REPOSITORY_CONSTITUTION.md",
            "system/runtime/repository_state/latest.json",
            "system/runtime/repository_constitution/constitution.json",
            "system/runtime/validation/validation_report.json",
            "packs/",
            "wbs/",
        ]
        return PlanningStateProjection(
            mission=project.get("Mission", "Build an AI Native Company."),
            long_term_goal=project.get("Vision", "Knowledge First"),
            current_phase=state.get("Current Phase", project.get("Current Phase", "unknown")),
            current_objective=project.get("Current Objective", state.get("Next Action", "unknown")),
            current_scope=roadmap.get("scope", "repository-managed planning"),
            current_pack=current_pack,
            current_ep=current_ep,
            wbs=self._read_wbs(),
            approved_next_action=repo_state.get("next_action", state.get("Next Action", "unknown")),
            parking_lot=parking_lot,
            refactoring_priorities=refactoring_priorities,
            blocked_items=blocked_items,
            approval_required=bool(repo_state.get("approval_required", False)),
            source_artifacts=source_artifacts,
        )

    def write(self, state: PlanningStateProjection) -> None:
        runtime_dir = self.base_path / "runtime" / "planning"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(state)
        (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (runtime_dir / "latest.md").write_text(self._to_markdown(state), encoding="utf-8")
        (runtime_dir / "planning_state.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (runtime_dir / "PLANNING_STATE.md").write_text(self._to_markdown(state), encoding="utf-8")

    def _to_markdown(self, state: PlanningStateProjection) -> str:
        return "\n".join([
            "# PLANNING_STATE",
            "",
            f"mission: {state.mission}",
            f"long_term_goal: {state.long_term_goal}",
            f"current_phase: {state.current_phase}",
            f"current_objective: {state.current_objective}",
            f"current_scope: {state.current_scope}",
            f"current_pack: {state.current_pack}",
            f"current_ep: {state.current_ep}",
            f"approved_next_action: {state.approved_next_action}",
            f"approval_required: {str(state.approval_required).lower()}",
            "",
        ])

    def _parse_key_values(self, path: Path) -> dict[str, str]:
        if not path.exists():
            return {}
        values: dict[str, str] = {}
        current_key = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                current_key = line[3:].strip()
            elif current_key and line and not line.startswith("#") and not line.startswith("-") and ":" not in line:
                values[current_key] = line.strip()
        return values

    def _parse_state(self, path: Path) -> dict[str, str]:
        if not path.exists():
            return {}
        values: dict[str, str] = {}
        current_key = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# ") and current_key is None:
                continue
            if line.startswith("## "):
                current_key = line[3:].strip()
            elif current_key and line and not line.startswith("-") and ":" not in line:
                values[current_key] = line.strip()
        return values

    def _parse_roadmap(self, path: Path) -> dict[str, str]:
        if not path.exists():
            return {}
        lines = path.read_text(encoding="utf-8").splitlines()
        return {"scope": lines[2].strip() if len(lines) > 2 else "repository-managed planning"}

    def _read_wbs(self) -> list[str]:
        wbs_dir = self.base_path / "wbs"
        if not wbs_dir.exists():
            return []
        return sorted(path.name for path in wbs_dir.glob("WBS-*.md"))

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_pack_ids(self) -> list[str]:
        registry = self.base_path / "packs" / "registry.yaml"
        if not registry.exists():
            return []
        ids: list[str] = []
        for line in registry.read_text(encoding="utf-8").splitlines():
            if line.startswith("- pack_id:"):
                ids.append(line.split(":", 1)[1].strip())
        return ids

    def _blocked_items(self, repo_state: dict, validation: dict) -> list[str]:
        items: list[str] = []
        if repo_state.get("approval_required"):
            items.append("approval_required")
        if validation.get("overall_success") is False:
            items.append("validation_failure")
        return items

    def _parking_lot(self, repo_state: dict, packs: list[str]) -> list[str]:
        lot: list[str] = []
        if repo_state.get("queue_status") not in {"READY", "DONE"}:
            lot.append(f"queue:{repo_state.get('queue_status')}")
        if not packs:
            lot.append("packs:missing")
        return lot

    def _refactoring_priorities(self, repo_state: dict, constitution: dict) -> list[str]:
        priorities = [
            "mission_alignment",
            "risk_reduction",
            "management_cost_reduction",
        ]
        if constitution.get("status") != "stable":
            priorities.append("constitution_freeze")
        if repo_state.get("repository_health") != "healthy":
            priorities.append("repository_health_repair")
        return priorities
