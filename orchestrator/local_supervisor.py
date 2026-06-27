from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from urllib.request import Request, urlopen
from urllib.error import URLError


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
        work_planner = self._read_json(self.base_path / "runtime" / "work_planner" / "latest.json")
        acceptance = self._read_json(self.base_path / "runtime" / "product_acceptance" / "acceptance_0001.json")
        if not planning:
            raise LocalSupervisorError("Missing planning state")
        if not repository:
            raise LocalSupervisorError("Missing repository state")
        if repository.get("approval_required"):
            raise LocalSupervisorError("Repository state requires approval")
        next_item = self._select_next_work_item(planning, repository, work_planner, acceptance)
        execution_mode = "execute" if execution_flag else "dry_run"
        if execution_mode == "execute" and not execution_flag:
            raise LocalSupervisorError("Execution requires explicit local approval flag")
        execution_request = self._build_execution_request(next_item, work_planner, planning, acceptance)
        codex_intake_payload = {
            "mission": planning.get("mission"),
            "current_objective": planning.get("current_objective"),
            "current_pack": planning.get("current_pack"),
            "current_ep": planning.get("current_ep"),
            "next_action": next_item,
            "execution_request": execution_request,
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
        self._write_execution_request(execution_request)
        return result

    def _select_next_work_item(self, planning: dict, repository: dict, work_planner: dict, acceptance: dict) -> str:
        if acceptance and acceptance.get("issue_number") == 28:
            if acceptance.get("state") == "open":
                return f"Issue #28: {acceptance.get('title', 'ACCEPTANCE-0001')}"
            return acceptance.get("next_action") or "ACCEPTANCE-0001 completed; select next eligible work item."
        candidates = work_planner.get("candidate_items") or []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            if candidate.get("status") in {"completed", "done", "closed"}:
                continue
            if candidate.get("title"):
                return str(candidate["title"])
        return planning.get("approved_next_action") or repository.get("next_action") or "unknown"

    def _build_execution_request(self, next_item: str, work_planner: dict, planning: dict, acceptance: dict) -> dict:
        issue = acceptance if acceptance and acceptance.get("issue_number") == 28 else self._fetch_issue_28()
        request_id = "REQ-ACCEPTANCE-0001" if issue and issue.get("state") == "open" else "REQ-PLANNED-0001"
        return {
            "request_id": request_id,
            "request_status": "ready",
            "request_priority": 100,
            "approval_required": False,
            "dependency": [
                "runtime/planning/latest.json",
                "runtime/repository_state/latest.json",
                "runtime/work_planner/latest.json",
            ],
            "worker_assignment": "Codex",
            "next_action": next_item,
            "objective": planning.get("current_objective", "unknown"),
            "candidate_source": work_planner.get("candidate_items", []),
            "issue_number": 28 if issue and issue.get("state") == "open" else None,
        }

    def _write_execution_request(self, request: dict) -> None:
        runtime_dir = self.base_path / "runtime" / "request"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        (runtime_dir / "execution_request.json").write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (runtime_dir / "EXECUTION_REQUEST.md").write_text(
            "\n".join([
                "# EXECUTION_REQUEST",
                "",
                f"request_id: {request['request_id']}",
                f"request_status: {request['request_status']}",
                f"request_priority: {request['request_priority']}",
                f"approval_required: {str(request['approval_required']).lower()}",
                f"worker_assignment: {request['worker_assignment']}",
                f"next_action: {request['next_action']}",
                "",
            ]),
            encoding="utf-8",
        )

    def _fetch_issue_28(self) -> dict:
        url = "https://api.github.com/repos/macyvvv/acip/issues/28"
        try:
            request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "acip-local-supervisor"})
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, ValueError):
            return {}

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
