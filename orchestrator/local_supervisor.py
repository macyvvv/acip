from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass(frozen=True)
class LocalSupervisorResult:
    planning_status: str
    repository_status: str
    next_eligible_work_item: str
    codex_intake_payload: dict
    execution_mode: str
    approval_required: bool
    safety_gate: str
    source_artifacts: list[str]


class LocalSupervisorError(ValueError):
    pass


class LocalSupervisor:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self, *, execution_flag: bool = False) -> LocalSupervisorResult:
        planning = self._read_json(self.base_path / "runtime" / "planning" / "latest.json")
        repository = self._read_json(self.base_path / "runtime" / "repository_state" / "latest.json")
        if not planning:
            raise LocalSupervisorError("Missing planning state")
        if not repository:
            raise LocalSupervisorError("Missing repository state")
        if repository.get("approval_required"):
            raise LocalSupervisorError("Repository state requires approval")
        next_item = planning.get("approved_next_action") or repository.get("next_action") or "unknown"
        execution_mode = "execute" if execution_flag else "dry_run"
        if execution_mode == "execute" and not execution_flag:
            raise LocalSupervisorError("Execution requires explicit local approval flag")
        codex_intake_payload = {
            "mission": planning.get("mission"),
            "current_objective": planning.get("current_objective"),
            "current_pack": planning.get("current_pack"),
            "current_ep": planning.get("current_ep"),
            "next_action": next_item,
        }
        result = LocalSupervisorResult(
            planning_status="loaded",
            repository_status=repository.get("repository_health", "unknown"),
            next_eligible_work_item=next_item,
            codex_intake_payload=codex_intake_payload,
            execution_mode=execution_mode,
            approval_required=bool(repository.get("approval_required", False)),
            safety_gate="dry_run" if not execution_flag else "approved",
            source_artifacts=[
                "runtime/planning/latest.json",
                "runtime/repository_state/latest.json",
                "runtime/handoff/latest.json",
                "runtime/handoff/completion/latest.json",
                "runtime/event_runtime/",
                "queue/",
            ],
        )
        self._write_runtime(result)
        return result

    def _write_runtime(self, result: LocalSupervisorResult) -> None:
        runtime_dir = self.base_path / "runtime" / "supervisor"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(result)
        (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (runtime_dir / "latest.md").write_text(self._to_markdown(result), encoding="utf-8")

    def _to_markdown(self, result: LocalSupervisorResult) -> str:
        return "\n".join([
            "# LOCAL_AGENT_SUPERVISOR",
            "",
            f"planning_status: {result.planning_status}",
            f"repository_status: {result.repository_status}",
            f"next_eligible_work_item: {result.next_eligible_work_item}",
            f"execution_mode: {result.execution_mode}",
            f"approval_required: {str(result.approval_required).lower()}",
            f"safety_gate: {result.safety_gate}",
            "",
        ])

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
