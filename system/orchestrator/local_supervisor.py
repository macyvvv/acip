from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from urllib.request import Request, urlopen
from urllib.error import URLError


@dataclass(frozen=True)
class LocalSupervisorResult:
    supervisor_state: str
    planning_status: str
    repository_status: str
    next_eligible_work_item: str | None
    selected_issue_number: int | None
    selected_issue_title: str | None
    selection_reason: str
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

    def _path(self, *parts: str) -> Path:
        system_path = self.base_path / "system" / Path(*parts)
        legacy_path = self.base_path / Path(*parts)
        return system_path if system_path.exists() or not legacy_path.exists() else legacy_path

    def run(self, *, execution_flag: bool = False) -> LocalSupervisorResult:
        planning = self._read_json(self._path("runtime", "planning", "latest.json"))
        repository = self._read_json(self._path("runtime", "repository_state", "latest.json"))
        work_planner = self._read_json(self._path("runtime", "work_planner", "latest.json"))
        acceptance = self._read_json(self._path("runtime", "product_acceptance", "acceptance_0001.json"))
        completed_issue_numbers = self._completed_issue_numbers()
        if not planning:
            raise LocalSupervisorError("Missing planning state")
        if not repository:
            raise LocalSupervisorError("Missing repository state")
        if repository.get("approval_required"):
            raise LocalSupervisorError("Repository state requires approval")
        open_issues = self._load_open_issues()
        open_issues = [issue for issue in open_issues if issue.get("number") not in completed_issue_numbers]
        self._write_open_issues(open_issues)
        next_item, selected_issue_number, selected_issue_title, selection_reason = self._select_next_work_item(
            planning,
            repository,
            work_planner,
            acceptance,
            open_issues,
        )
        execution_mode = "execute" if execution_flag else "dry_run"
        if execution_mode == "execute" and not execution_flag:
            raise LocalSupervisorError("Execution requires explicit local approval flag")
        execution_request = self._build_execution_request(
            next_item,
            selected_issue_number,
            selected_issue_title,
            work_planner,
            planning,
            acceptance,
        )
        codex_intake_payload = {
            "mission": planning.get("mission"),
            "current_objective": planning.get("current_objective"),
            "current_pack": planning.get("current_pack"),
            "current_ep": planning.get("current_ep"),
            "next_action": next_item,
            "execution_request": execution_request,
        }
        result = LocalSupervisorResult(
            supervisor_state="ready" if next_item else "idle",
            planning_status="loaded",
            repository_status=repository.get("repository_health", "unknown"),
            next_eligible_work_item=next_item,
            selected_issue_number=selected_issue_number,
            selected_issue_title=selected_issue_title,
            selection_reason=selection_reason,
            codex_intake_payload=codex_intake_payload,
            execution_mode=execution_mode,
            approval_required=bool(repository.get("approval_required", False)),
            safety_gate="dry_run" if not execution_flag else "approved",
            source_artifacts=[
                "system/runtime/planning/latest.json",
                "system/runtime/repository_state/latest.json",
                "system/runtime/handoff/latest.json",
                "system/runtime/handoff/completion/latest.json",
                "system/runtime/event_runtime/",
                "queue/",
                "system/runtime/github/",
                "system/runtime/issues/",
            ],
        )
        self._write_runtime(result)
        self._write_execution_request(execution_request)
        return result

    def _select_next_work_item(
        self,
        planning: dict,
        repository: dict,
        work_planner: dict,
        acceptance: dict,
        open_issues: list[dict],
    ) -> tuple[str | None, int | None, str | None, str]:
        if acceptance and acceptance.get("issue_number") == 28:
            if acceptance.get("state") == "open":
                title = acceptance.get("title", "ACCEPTANCE-0001")
                return f"Issue #28: {title}", 28, title, "acceptance_issue_open"
            return self._select_issue_from_open_issues(open_issues)
        return self._select_issue_from_open_issues(open_issues, work_planner)

    def _select_issue_from_open_issues(
        self,
        open_issues: list[dict],
        work_planner: dict | None = None,
    ) -> tuple[str | None, int | None, str | None, str]:
        eligible_issues = [issue for issue in open_issues if self._is_eligible_issue(issue)]
        if eligible_issues:
            selected = self._choose_issue(eligible_issues)
            title = str(selected.get("title", "")).strip()
            issue_number = int(selected.get("number"))
            return f"Issue #{issue_number}: {title}", issue_number, title, "issue_intake"
        candidates = (work_planner or {}).get("candidate_items") or []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            if candidate.get("status") in {"completed", "done", "closed"}:
                continue
            if candidate.get("title"):
                return str(candidate["title"]), None, str(candidate["title"]), "work_planner_candidate"
        return None, None, None, "idle_no_eligible_candidate"

    def _build_execution_request(
        self,
        next_item: str | None,
        selected_issue_number: int | None,
        selected_issue_title: str | None,
        work_planner: dict,
        planning: dict,
        acceptance: dict,
    ) -> dict:
        issue = acceptance if acceptance and acceptance.get("issue_number") == 28 else self._fetch_issue_28()
        request_id = (
            "REQ-ACCEPTANCE-0001"
            if selected_issue_number == 28
            else f"REQ-ISSUE-{selected_issue_number:04d}"
            if selected_issue_number is not None
            else ("REQ-ACCEPTANCE-0001" if issue and issue.get("state") == "open" else "REQ-PLANNED-0001")
        )
        return {
            "request_id": request_id,
            "request_status": "ready",
            "request_priority": 100,
            "approval_required": False,
            "dependency": [
                "system/runtime/planning/latest.json",
                "system/runtime/repository_state/latest.json",
                "system/runtime/work_planner/latest.json",
            ],
            "worker_assignment": "Codex",
            "next_action": next_item,
            "objective": planning.get("current_objective", "unknown"),
            "candidate_source": work_planner.get("candidate_items", []),
            "issue_number": selected_issue_number if selected_issue_number is not None else (28 if issue and issue.get("state") == "open" else None),
            "issue_title": selected_issue_title,
        }

    def _write_execution_request(self, request: dict) -> None:
        for runtime_dir in (self.base_path / "system" / "runtime" / "request", self.base_path / "runtime" / "request"):
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

    def _load_open_issues(self) -> list[dict]:
        candidates: list[dict] = []
        for path in [
            self._path("runtime", "github", "open_issues.json"),
            self._path("runtime", "issues", "open_issues.json"),
        ]:
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        candidates.extend(issue for issue in data if isinstance(issue, dict))
                except json.JSONDecodeError:
                    continue
        if candidates:
            return candidates
        return self._fetch_open_issues_from_github()

    def _write_open_issues(self, issues: list[dict]) -> None:
        for runtime_dir in (self.base_path / "system" / "runtime" / "github", self.base_path / "runtime" / "github"):
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "open_issues.json").write_text(json.dumps(issues, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _completed_issue_numbers(self) -> set[int]:
        completed_numbers: set[int] = set()
        completed_dir = self.base_path / "runtime" / "issues" / "completed"
        if not completed_dir.exists():
            return completed_numbers
        for path in completed_dir.glob("issue_*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(data.get("issue_number"), int):
                completed_numbers.add(int(data["issue_number"]))
        return completed_numbers

    def _fetch_open_issues_from_github(self) -> list[dict]:
        url = "https://api.github.com/repos/macyvvv/acip/issues?state=open&per_page=100"
        try:
            request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "acip-local-supervisor"})
            with urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data if isinstance(data, list) else []
        except (URLError, TimeoutError, ValueError):
            return []

    def _is_eligible_issue(self, issue: dict) -> bool:
        number = issue.get("number")
        title = str(issue.get("title", ""))
        state = issue.get("state")
        if not isinstance(number, int) or state != "open":
            return False
        if number == 28:
            return False
        upper_title = title.upper()
        if upper_title.startswith("PRODUCT-") or upper_title.startswith("CONTENT-"):
            return True
        if upper_title.startswith("PACK-") or upper_title.startswith("FIX-"):
            return bool(issue.get("allow_pack_fix", False))
        return False

    def _choose_issue(self, issues: list[dict]) -> dict:
        def category(issue: dict) -> tuple[int, int]:
            title = str(issue.get("title", "")).upper()
            if title.startswith("PRODUCT-"):
                group = 0
            elif title.startswith("CONTENT-"):
                group = 1
            elif title.startswith("PACK-") or title.startswith("FIX-"):
                group = 2
            else:
                group = 3
            return (group, int(issue.get("number", 0)))

        return sorted(issues, key=category)[0]

    def _write_runtime(self, result: LocalSupervisorResult) -> None:
        payload = asdict(result)
        for runtime_dir in (self.base_path / "system" / "runtime" / "supervisor", self.base_path / "runtime" / "supervisor"):
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (runtime_dir / "latest.md").write_text(self._to_markdown(result), encoding="utf-8")

    def _to_markdown(self, result: LocalSupervisorResult) -> str:
        return "\n".join([
            "# LOCAL_AGENT_SUPERVISOR",
            "",
            f"supervisor_state: {result.supervisor_state}",
            f"planning_status: {result.planning_status}",
            f"repository_status: {result.repository_status}",
            f"next_eligible_work_item: {result.next_eligible_work_item if result.next_eligible_work_item is not None else 'null'}",
            f"selected_issue_number: {result.selected_issue_number if result.selected_issue_number is not None else 'null'}",
            f"selected_issue_title: {result.selected_issue_title if result.selected_issue_title is not None else 'null'}",
            f"selection_reason: {result.selection_reason}",
            f"execution_mode: {result.execution_mode}",
            f"approval_required: {str(result.approval_required).lower()}",
            f"safety_gate: {result.safety_gate}",
            "",
        ])

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
