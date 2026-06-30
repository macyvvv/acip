from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

from system.core.failure_learning import load_failure_rules
from system.core.failure_store import load_failures
from system.core.optimization_advisor import analyze_optimization_opportunities


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
    applied_learning_rule: dict | None
    learning_reason: str
    optimization_applied: bool
    optimization_type: str | None
    optimization_reason: str | None
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
        next_item = planning.get("next_item")
        open_issues = self._load_open_issues()
        open_issues = [issue for issue in open_issues if issue.get("number") not in completed_issue_numbers]
        failure_rules = load_failure_rules(self.base_path)
        failures = load_failures(self.base_path)
        rule_skipped_issue_numbers = self._rule_skipped_issue_numbers(open_issues, failure_rules, failures)
        skipped_issue_numbers = self._skipped_issue_numbers(open_issues, failures)
        skipped_issue_numbers |= rule_skipped_issue_numbers
        open_issues = [issue for issue in open_issues if issue.get("number") not in skipped_issue_numbers]
        self._write_open_issues(open_issues)
        selected_issue_number = None
        selected_issue_title = None
        selection_reason = "planning_next_item"
        if not next_item:
            next_item, selected_issue_number, selected_issue_title, selection_reason = self._select_next_work_item(
                planning,
                repository,
                work_planner,
                acceptance,
                open_issues,
                failure_rules,
                failures,
            )
        if selected_issue_number is not None and selected_issue_title is not None:
            next_item = f"Issue #{selected_issue_number}: {selected_issue_title}"
        applied_learning_rule = self._applied_learning_rule(open_issues, failure_rules, skipped_issue_numbers, selected_issue_number)
        learning_reason = self._learning_reason(applied_learning_rule)
        optimization_applied, optimization_type, optimization_reason, execution_request = self._apply_optimization(
            planning,
            repository,
            selected_issue_number,
            selected_issue_title,
            work_planner,
            acceptance,
            next_item,
        )
        if skipped_issue_numbers and next_item is not None:
            selection_reason = "skipped_due_to_failure_history"
        execution_mode = "execute" if execution_flag else "dry_run"
        if execution_mode == "execute" and not execution_flag:
            raise LocalSupervisorError("Execution requires explicit local approval flag")
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
            applied_learning_rule=applied_learning_rule,
            learning_reason=learning_reason,
            optimization_applied=optimization_applied,
            optimization_type=optimization_type,
            optimization_reason=optimization_reason,
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

    def _skipped_issue_numbers(self, issues: list[dict], failures: list[dict]) -> set[int]:
        skipped: set[int] = set()
        for issue in issues:
            issue_number = issue.get("number")
            if not isinstance(issue_number, int):
                continue
            entry = self._last_failure_for_issue(failures, issue_number)
            rule = self._matching_rule(issue_number, str(entry.get("error_type", "external_capacity")) if entry else "external_capacity")
            if rule is None:
                continue
            if rule.get("action") not in {"skip", "temporary_skip"}:
                continue
            if int(rule.get("threshold", 0)) < 3:
                continue
            if entry and self._cooldown_expired(rule, entry):
                continue
            skipped.add(issue_number)
        return skipped

    def _rule_skipped_issue_numbers(self, issues: list[dict], rules: list[dict], failures: list[dict]) -> set[int]:
        skipped: set[int] = set()
        for rule in rules:
            issue_number = rule.get("issue_number")
            if not isinstance(issue_number, int):
                continue
            issue = self._issue_by_number(issues, issue_number)
            if issue is None:
                continue
            if rule.get("action") not in {"skip", "temporary_skip"}:
                continue
            if int(rule.get("threshold", 0)) < 3:
                continue
            failure_entry = self._last_failure_for_issue(failures, issue_number)
            if failure_entry and self._cooldown_expired(rule, failure_entry):
                continue
            skipped.add(issue_number)
        return skipped

    def _applied_learning_rule(
        self,
        issues: list[dict],
        rules: list[dict],
        skipped_issue_numbers: set[int],
        selected_issue_number: int | None,
    ) -> dict | None:
        if not skipped_issue_numbers:
            return None
        for rule in rules:
            issue_number = rule.get("issue_number")
            if issue_number in skipped_issue_numbers and rule.get("action") == "skip":
                return {
                    "issue_number": int(rule.get("issue_number", 0)),
                    "error_type": str(rule.get("error_type", "")),
                    "threshold": int(rule.get("threshold", 0)),
                }
        return None

    def _learning_reason(self, applied_learning_rule: dict | None) -> str:
        if not applied_learning_rule:
            return ""
        issue_number = applied_learning_rule.get("issue_number")
        error_type = applied_learning_rule.get("error_type")
        threshold = applied_learning_rule.get("threshold")
        return f"issue {issue_number} skipped due to repeated {error_type} failures (threshold {threshold})"

    def _apply_optimization(
        self,
        planning: dict,
        repository: dict,
        selected_issue_number: int | None,
        selected_issue_title: str | None,
        work_planner: dict,
        acceptance: dict,
        next_item: str | None,
    ) -> tuple[bool, str | None, str | None, dict]:
        config = self._read_json(self._path("runtime", "config", "optimization.json"))
        if not config.get("enabled", False):
            return False, None, None, self._build_execution_request(next_item, selected_issue_number, selected_issue_title, work_planner, planning, acceptance)
        suggestions = analyze_optimization_opportunities(self.base_path)
        if not suggestions:
            return False, None, None, self._build_execution_request(next_item, selected_issue_number, selected_issue_title, work_planner, planning, acceptance)
        suggestion = next((item for item in suggestions if item.get("type") in set(config.get("allowed_types", []))), None)
        if suggestion is None:
            return False, None, None, self._build_execution_request(next_item, selected_issue_number, selected_issue_title, work_planner, planning, acceptance)
        if suggestion.get("type") != "model_selection":
            return False, None, None, self._build_execution_request(next_item, selected_issue_number, selected_issue_title, work_planner, planning, acceptance)
        last_execution = self._read_json(self._path("runtime", "local_execution", "latest.json"))
        if last_execution.get("failure_reason") and self._is_optimized_failure(last_execution):
            return False, None, None, self._build_execution_request(next_item, selected_issue_number, selected_issue_title, work_planner, planning, acceptance)
        execution_request = self._build_execution_request(next_item, selected_issue_number, selected_issue_title, work_planner, planning, acceptance)
        original_model = execution_request.get("preferred_model") or execution_request.get("model_override") or "gpt-5.4-mini"
        optimized_model = self._downgrade_model_one_level(str(original_model))
        if optimized_model == original_model:
            return False, None, None, execution_request
        execution_request["preferred_model"] = original_model
        execution_request["model_override"] = optimized_model
        return True, "model_selection", "high external_capacity failure rate", execution_request

    def _matching_rule(self, issue_number: int, error_type: str, failure_rules: list[dict] | None = None) -> dict | None:
        for rule in failure_rules if failure_rules is not None else load_failure_rules(self.base_path):
            if rule.get("issue_number") == issue_number and rule.get("error_type") == error_type:
                return rule
        return None

    def _cooldown_expired(self, rule: dict, failure_entry: dict) -> bool:
        cooldown_seconds = int(rule.get("cooldown_seconds", 0))
        if cooldown_seconds <= 0:
            return False
        last_failed_at = str(failure_entry.get("last_failed_at") or failure_entry.get("timestamp") or "")
        if not last_failed_at:
            return False
        try:
            parsed = datetime.fromisoformat(last_failed_at)
        except ValueError:
            return False
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - parsed).total_seconds() >= cooldown_seconds

    def _issue_by_number(self, issues: list[dict], issue_number: int) -> dict | None:
        for issue in issues:
            if issue.get("number") == issue_number:
                return issue
        return None

    def _is_optimized_failure(self, last_execution: dict) -> bool:
        resolved_model = str(last_execution.get("resolved_model", ""))
        failure_reason = str(last_execution.get("failure_reason", ""))
        return bool(resolved_model == "gpt-5.3-mini" and failure_reason)

    def _downgrade_model_one_level(self, model: str) -> str:
        order = ["gpt-5.4", "gpt-5.4-mini", "gpt-5.3-mini", "gpt-5.2-mini"]
        if model not in order:
            return model
        index = order.index(model)
        if index + 1 >= len(order):
            return model
        return order[index + 1]

    def _last_failure_for_issue(self, failures: list[dict], issue_number: int) -> dict | None:
        for entry in reversed(failures):
            if entry.get("issue_number") == issue_number:
                return entry
        return None

    def _select_next_work_item(
        self,
        planning: dict,
        repository: dict,
        work_planner: dict,
        acceptance: dict,
        open_issues: list[dict],
        failure_rules: list[dict],
        failures: list[dict],
    ) -> tuple[str | None, int | None, str | None, str]:
        if acceptance and acceptance.get("issue_number") == 28:
            if acceptance.get("state") == "open":
                title = acceptance.get("title", "ACCEPTANCE-0001")
                return f"Issue #28: {title}", 28, title, "acceptance_issue_open"
            return self._select_issue_from_open_issues(open_issues, None, failure_rules, failures)
        return self._select_issue_from_open_issues(open_issues, work_planner, failure_rules, failures)

    def _select_issue_from_open_issues(
        self,
        open_issues: list[dict],
        work_planner: dict | None = None,
        failure_rules: list[dict] | None = None,
        failures: list[dict] | None = None,
    ) -> tuple[str | None, int | None, str | None, str]:
        eligible_issues = []
        for issue in open_issues:
            if not self._is_eligible_issue(issue):
                continue
            issue_number = int(issue.get("number", 0))
            rule = self._matching_rule(issue_number, "external_capacity", failure_rules)
            entry = self._last_failure_for_issue(failures or [], issue_number)
            if rule and entry and not self._cooldown_expired(rule, entry):
                continue
            eligible_issues.append(issue)
        if eligible_issues:
            selected = self._choose_issue(eligible_issues)
            title = str(selected.get("title", "")).strip()
            issue_number = int(selected.get("number"))
            selection_reason = "issue_intake"
            if self._cooldown_reenabled(issue_number):
                selection_reason = "cooldown_expired_retry"
            return f"Issue #{issue_number}: {title}", issue_number, title, selection_reason
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
            "preferred_model": "gpt-5.4-mini",
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
        state = str(issue.get("state", "")).strip().lower()
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

    def _cooldown_reenabled(self, issue_number: int) -> bool:
        failures = load_failures(self.base_path)
        entry = self._last_failure_for_issue(failures, issue_number)
        if not entry:
            return False
        rule = self._matching_rule(issue_number, str(entry.get("error_type", "")))
        if not rule:
            return False
        return self._cooldown_expired(rule, entry)

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
            f"applied_learning_rule: {json.dumps(result.applied_learning_rule, ensure_ascii=False) if result.applied_learning_rule is not None else 'null'}",
            f"learning_reason: {result.learning_reason if result.learning_reason else 'null'}",
            f"optimization_applied: {str(result.optimization_applied).lower()}",
            f"optimization_type: {result.optimization_type if result.optimization_type is not None else 'null'}",
            f"optimization_reason: {result.optimization_reason if result.optimization_reason is not None else 'null'}",
            "",
        ])

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
