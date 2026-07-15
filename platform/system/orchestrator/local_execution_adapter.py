from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess

from system.core.failure_store import append_failure
from system.core.failure_learning import write_failure_rules
from system.core.kpi_store import update_kpi
from system.core.optimization_advisor import write_optimization_suggestions


# Claude Code headless execution. Claude Code covers both the implementation and
# review work that ChatGPT + Codex used to split, so the adapter drives a single
# `claude -p` invocation instead of the old two-service `codex exec` handoff.
DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_SUPPORTED_MODELS = ["claude-haiku-4-5", "claude-sonnet-5", "claude-opus-4-8"]
DEFAULT_CLI_TIMEOUT_SECONDS = 60


@dataclass(frozen=True)
class LocalExecutionResult:
    adapter_mode: str
    approval_required: bool
    execution_gate: str
    agent_cli_command: str
    request_id: str
    request_status: str
    repository_health: str
    validation_status: str
    worktree_state: str
    resolved_model: str | None
    model_policy: str
    model_resolution_reason: str
    stdout: str
    stderr: str
    exit_code: int
    captured_at: str
    source_artifacts: list[str]
    blocked_by_usage_limit: bool
    failure_reason: str | None
    model_attempts: list[dict]


class LocalExecutionError(ValueError):
    pass


class LocalExecutionAdapter:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self, *, approval_flag: bool = False, dry_run: bool = True) -> LocalExecutionResult:
        supervisor = self._read_json(self._runtime_path("supervisor", "latest.json"))
        planning = self._read_json(self._runtime_path("planning", "latest.json"))
        repository = self._read_json(self._runtime_path("repository_state", "latest.json"))
        request = self._read_request()

        # There is no autonomous supervisor daemon anymore; requests normally come
        # straight from the approved issue/draft handoff (agent_issue_bridge.py).
        # supervisor/latest.json is only needed as a fallback source when no
        # request has been written yet.
        if request is None and not supervisor:
            raise LocalExecutionError("Missing supervisor output")
        if not planning:
            raise LocalExecutionError("Missing planning state")
        if not repository:
            raise LocalExecutionError("Missing repository state")
        if repository.get("worktree_state") not in {"clean", "unknown"}:
            raise LocalExecutionError("Refusing execution on dirty worktree")
        if repository.get("validation_status") not in {"success", "unknown"}:
            raise LocalExecutionError("Refusing execution with failing validation state")
        if repository.get("approval_required") and not approval_flag:
            raise LocalExecutionError("Approval required for execution")
        if not dry_run and not approval_flag:
            raise LocalExecutionError("Real execution requires explicit approval flag")

        if request is None:
            request = self._derive_request(supervisor)
        self._validate_alignment(planning, request)

        prompt = self._render_prompt(request, planning, repository)
        prompt_path = self._write_prompt(prompt)
        model_resolution = self._resolve_model(request, planning, repository)
        if model_resolution.get("resolved_model") is None:
            failure_reason = str(model_resolution.get("failure_reason", "no_supported_model"))
            self._write_model_resolution(model_resolution)
            result = self._result(
                repository=repository,
                request=request,
                adapter_mode="dry_run" if dry_run else "execute",
                execution_gate="closed" if dry_run else "open",
                command=[],
                stdout="",
                stderr=failure_reason,
                exit_code=1,
                prompt_path=prompt_path,
                model_resolution=model_resolution,
                blocked_by_usage_limit=False,
                failure_reason=failure_reason,
                model_attempts=[],
            )
            self._write_runtime(result)
            raise LocalExecutionError(failure_reason)

        command = self._build_command(prompt_path, model_resolution["resolved_model"])
        self._write_model_resolution(model_resolution)
        adapter_mode = "dry_run" if dry_run else "execute"
        execution_gate = "closed" if dry_run else "open"
        stdout = "dry-run only"
        stderr = ""
        exit_code = 0
        failure_reason = ""
        model_attempts: list[dict] = []
        try:
            if not dry_run:
                stdout, stderr, exit_code, model_attempts = self._run_with_model_fallback(prompt_path, model_resolution["resolved_model"], request, planning, repository)
                if exit_code != 0:
                    raise LocalExecutionError(f"Claude command failed: {exit_code}")
                deliverable_check = self._verify_deliverables(request)
                if not deliverable_check["ok"]:
                    raise LocalExecutionError("missing_deliverables")
        except Exception as exc:
            blocked_by_usage_limit = self._is_usage_limit_error(exc) or self._is_usage_limit_error(stderr)
            failure_reason = "blocked_by_usage_limit" if blocked_by_usage_limit else str(exc)
            if failure_reason == "missing_deliverables":
                blocked_by_usage_limit = False
            self._record_failure(request, model_resolution, stderr, failure_reason)
            write_failure_rules(self.base_path)
            result = self._result(
                repository=repository,
                request=request,
                adapter_mode=adapter_mode,
                execution_gate=execution_gate,
                command=command,
                stdout=stdout,
                stderr=str(exc) if not stderr else stderr,
                exit_code=exit_code or 1,
                prompt_path=prompt_path,
                model_resolution=model_resolution,
                blocked_by_usage_limit=blocked_by_usage_limit,
                failure_reason=failure_reason,
                model_attempts=model_attempts,
            )
            self._write_runtime(result)
            update_kpi(False, self.base_path, issue_number=int(request.get("issue_number") or 0) or None, error_type=self._classify_error(stderr, failure_reason))
            raise

        result = self._result(
            repository=repository,
            request=request,
            adapter_mode=adapter_mode,
            execution_gate=execution_gate,
            command=command,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            prompt_path=prompt_path,
            model_resolution=model_resolution,
            blocked_by_usage_limit=False,
            failure_reason=None,
            model_attempts=model_attempts,
        )
        self._write_runtime(result)
        update_kpi(
            exit_code == 0 and result.failure_reason is None,
            self.base_path,
            issue_number=int(request.get("issue_number") or 0) or None,
            error_type=self._classify_error(stderr, failure_reason),
        )
        write_optimization_suggestions(self.base_path)
        return result

    def _record_failure(self, request: dict, model_resolution: dict, stderr: str, failure_reason: str) -> None:
        issue_number = int(request.get("issue_number") or 0)
        if issue_number <= 0:
            return
        append_failure(
            {
                "request_id": request.get("request_id", ""),
                "issue_number": issue_number,
                "error_type": self._classify_error(stderr, failure_reason),
                "model": model_resolution.get("resolved_model") or "",
            },
            base_path=self.base_path,
        )

    def _classify_error(self, stderr: str, failure_reason: str) -> str:
        text = f"{stderr}\n{failure_reason}".lower()
        if "capacity" in text:
            return "external_capacity"
        if "usage limit" in text:
            return "usage_limit"
        if "not supported" in text:
            return "model_unsupported"
        return "unknown"

    def _derive_request(self, supervisor: dict) -> dict:
        payload = supervisor.get("intake_payload", {}) or supervisor.get("codex_intake_payload", {})
        return {
            "request_id": f"REQ-{payload.get('current_ep', 'UNKNOWN')}",
            "request_status": "ready",
            "request_priority": 0,
            "approval_required": False,
            "dependency": ["platform/system/runtime/supervisor/latest.json"],
            "worker_assignment": "Claude",
        }

    def _validate_alignment(self, planning: dict, request: dict) -> None:
        objective = planning.get("current_objective", "")
        if not objective:
            raise LocalExecutionError("Missing current objective")
        if request.get("request_status") not in {"ready", "pending_approval"}:
            raise LocalExecutionError("Invalid request status")

    def _render_prompt(self, request: dict, planning: dict, repository: dict) -> str:
        issue_instruction = self._issue_instruction(request)
        objective = request.get("objective") or planning.get("current_objective", "unknown")
        lines = [
            "# Claude Execution Prompt",
            "",
            f"Request ID: {request['request_id']}",
            f"Request Status: {request['request_status']}",
            f"Objective: {objective}",
            f"Selected Work Item: {request.get('next_action', 'unknown')}",
            f"Selected Issue Number: {request.get('issue_number', 'unknown')}",
            f"Selected Issue Title: {request.get('issue_title', 'unknown')}",
            "",
            issue_instruction,
            "Read platform/system/runtime/planning/latest.json, platform/system/runtime/repository_state/latest.json, platform/system/runtime/work_planner/latest.json, and platform/system/runtime/request/execution_request.json.",
            "Run:",
            "- python3 platform/system/platform/scripts/validate_all.py",
            "- python3 -m pytest -q",
            "- git status",
            "",
            "Do not auto-push.",
            "Do not modify Repository OS architecture.",
        ]
        return "\n".join(lines) + "\n"

    def _issue_instruction(self, request: dict) -> str:
        issue_number = request.get("issue_number")
        issue_title = request.get("issue_title")
        if issue_number is not None and issue_title:
            return f"Implement Issue #{issue_number} / {issue_title} using repository artifacts only."
        if issue_number is not None:
            return f"Implement Issue #{issue_number} using repository artifacts only."
        return "Implement the selected work item using repository artifacts only."

    def _write_prompt(self, prompt: str) -> Path:
        runtime_dir = self.base_path / "runtime" / "local_execution"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = runtime_dir / "agent_prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        return prompt_path

    def _resolve_model(self, request: dict, planning: dict, repository: dict) -> dict:
        policy = os.environ.get("CLAUDE_MODEL_POLICY", "cost_optimized")
        override = str(request.get("model_override") or os.environ.get("CLAUDE_MODEL_OVERRIDE", "")).strip()
        configured_models = self._supported_models()
        candidate_models = self._rank_models(configured_models, request, planning, repository, policy)

        if override:
            if override not in configured_models:
                candidate_models = [override] + candidate_models
            return self._resolved_model_resolution(
                policy=policy,
                candidate_models=candidate_models,
                resolved_model=override,
                selection_reason="local override",
            )

        if not candidate_models:
            return self._failed_model_resolution(policy=policy, candidate_models=candidate_models, reason="no_supported_model")

        resolved_model = candidate_models[0]
        selection_reason = f"capability={self._required_capability(request, planning, repository)}; policy={policy}"
        return self._resolved_model_resolution(
            policy=policy,
            candidate_models=candidate_models,
            resolved_model=resolved_model,
            selection_reason=selection_reason,
        )

    def _failed_model_resolution(self, *, policy: str, candidate_models: list[str], reason: str) -> dict:
        return {
            "model_policy": policy,
            "candidate_models": candidate_models,
            "supported_models": [],
            "resolved_model": None,
            "fallback_used": False,
            "estimated_cost_tier": None,
            "selection_reason": reason,
            "resolved_at": self._resolved_at(),
            "failure_reason": reason,
        }

    def _resolved_model_resolution(
        self,
        *,
        policy: str,
        candidate_models: list[str],
        resolved_model: str,
        selection_reason: str,
    ) -> dict:
        return {
            "model_policy": policy,
            "candidate_models": candidate_models,
            "supported_models": candidate_models,
            "resolved_model": resolved_model,
            "fallback_used": bool(candidate_models) and resolved_model != candidate_models[0],
            "estimated_cost_tier": self._cost_tier(resolved_model),
            "selection_reason": selection_reason,
            "resolved_at": self._resolved_at(),
            "failure_reason": None,
        }

    def _supported_models(self) -> list[str]:
        configured = os.environ.get("CLAUDE_SUPPORTED_MODELS", "").strip()
        if configured:
            return [model.strip() for model in configured.split(",") if model.strip()]
        return list(DEFAULT_SUPPORTED_MODELS)

    def _required_capability(self, request: dict, planning: dict, repository: dict) -> str:
        request_text = " ".join(str(request.get(key, "")) for key in ("request_id", "request_status", "next_action"))
        planning_text = " ".join(str(planning.get(key, "")) for key in ("current_objective", "current_pack", "current_ep"))
        if any(keyword in request_text.lower() or keyword in planning_text.lower() for keyword in ("architecture", "high-risk", "high risk", "approval")):
            return "high_reasoning"
        if repository.get("approval_required"):
            return "reasoning"
        return "cost_optimized"

    def _rank_models(self, supported: list[str], request: dict, planning: dict, repository: dict, policy: str) -> list[str]:
        required_capability = self._required_capability(request, planning, repository)
        # Minimum model tier per capability; higher-reasoning work floors out weaker models.
        capability_floor = {
            "cost_optimized": 0,
            "reasoning": 1,
            "high_reasoning": 2,
        }
        floor = capability_floor.get(required_capability, 0)
        candidates = [model for model in supported if self._model_cost_rank(model) >= floor]
        # cost_optimized/reasoning prefer the cheapest capable model; high_reasoning prefers the strongest.
        reverse = policy == "high_reasoning" or required_capability == "high_reasoning"
        candidates.sort(key=lambda model: (self._model_cost_rank(model), model), reverse=reverse)
        return candidates

    def _cost_tier(self, model: str) -> str:
        return {
            "claude-haiku-4-5": "low",
            "claude-sonnet-5": "medium",
            "claude-opus-4-8": "high",
        }.get(model, "medium")

    def _resolved_at(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _build_command(self, prompt_path: Path, model: str) -> list[str]:
        return ["claude", "-p", prompt_path.read_text(encoding="utf-8"), "--model", model]

    def _run_with_model_fallback(
        self,
        prompt_path: Path,
        initial_model: str,
        request: dict,
        planning: dict,
        repository: dict,
    ) -> tuple[str, str, int, list[dict]]:
        model_attempts: list[dict] = []
        fallback_chain = self._model_fallback_chain(initial_model)
        last_stdout = ""
        last_stderr = ""
        last_exit_code = 1
        for model in fallback_chain:
            command = self._build_command(prompt_path, model)
            completed = self._run_command(command)
            last_stdout = completed.stdout
            last_stderr = completed.stderr
            last_exit_code = completed.returncode
            if completed.returncode == 0 and self._verify_deliverables(request)["ok"]:
                model_attempts.append({"model": model, "result": "success"})
                self._write_model_attempts(model_attempts)
                return last_stdout, last_stderr, last_exit_code, model_attempts
            if self._is_capacity_error(last_stderr) or self._is_capacity_error(last_stdout) or self._is_capacity_error(last_exit_code):
                model_attempts.append({"model": model, "result": "capacity_fail"})
                if len(model_attempts) >= len(fallback_chain):
                    break
                continue
            model_attempts.append({"model": model, "result": "failure"})
            self._write_model_attempts(model_attempts)
            return last_stdout, last_stderr, last_exit_code, model_attempts
        self._write_model_attempts(model_attempts)
        return last_stdout, last_stderr, last_exit_code, model_attempts

    def _model_fallback_chain(self, initial_model: str) -> list[str]:
        # On capacity pressure, fall back to progressively cheaper models.
        chain = sorted(self._supported_models(), key=lambda model: (self._model_cost_rank(model), model), reverse=True)
        if initial_model in chain:
            return chain[chain.index(initial_model):]
        return [initial_model] + chain

    def _is_capacity_error(self, value: object) -> bool:
        return "capacity" in str(value).lower()

    def _is_usage_limit_error(self, value: object) -> bool:
        text = str(value).lower()
        return "usage limit" in text or "out of credits" in text

    def _model_cost_rank(self, model: str) -> int:
        order = {
            "claude-haiku-4-5": 0,
            "claude-sonnet-5": 1,
            "claude-opus-4-8": 2,
        }
        return order.get(model, 1)

    def _verify_deliverables(self, request: dict) -> dict:
        issue_number = request.get("issue_number")
        issue_title = str(request.get("issue_title", "")).upper()
        required_paths_by_issue = {
            30: [
                "platform/app/products/minimal_launch_brief_generator/README.md",
                "platform/app/products/minimal_launch_brief_generator/requirements.md",
                "platform/app/products/minimal_launch_brief_generator/architecture.md",
                "platform/app/products/minimal_launch_brief_generator/release_notes.md",
                "platform/app/products/minimal_launch_brief_generator/src/__init__.py",
                "platform/app/products/minimal_launch_brief_generator/src/minimal_launch_brief_generator.py",
                "platform/app/products/minimal_launch_brief_generator/tests/test_minimal_launch_brief_generator.py",
            ]
        }
        required_paths = required_paths_by_issue.get(issue_number, [])
        missing_paths = [path for path in required_paths if not (self.base_path / path).exists()]
        return {
            "ok": not missing_paths,
            "issue_number": issue_number,
            "issue_title": issue_title,
            "required_paths": required_paths,
            "missing_paths": missing_paths,
        }

    def _run_command(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        timeout_seconds = int(os.environ.get("CLAUDE_EXECUTION_TIMEOUT_SECONDS", str(DEFAULT_CLI_TIMEOUT_SECONDS)))
        try:
            return subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return subprocess.CompletedProcess(
                args=exc.cmd,
                returncode=124,
                stdout=stdout,
                stderr=stderr + f"\ncommand timed out after {timeout_seconds}s",
            )

    def _write_model_resolution(self, model_resolution: dict) -> None:
        runtime_dir = self._runtime_path("local_execution")
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            **model_resolution,
            "source_artifacts": [
                "platform/system/runtime/supervisor/latest.json",
                "platform/system/runtime/repository_state/latest.json",
                "platform/system/runtime/planning/latest.json",
                "platform/system/runtime/request/execution_request.json",
            ],
        }
        (runtime_dir / "model_resolution.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _write_model_attempts(self, model_attempts: list[dict]) -> None:
        runtime_dir = self._runtime_path("local_execution")
        runtime_dir.mkdir(parents=True, exist_ok=True)
        latest_path = runtime_dir / "latest.json"
        if latest_path.exists():
            payload = json.loads(latest_path.read_text(encoding="utf-8"))
            payload["model_attempts"] = model_attempts
            latest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            latest_md_path = runtime_dir / "latest.md"
            if latest_md_path.exists():
                latest_md_path.write_text(latest_md_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    def _result(
        self,
        *,
        repository: dict,
        request: dict,
        adapter_mode: str,
        execution_gate: str,
        command: list[str],
        stdout: str,
        stderr: str,
        exit_code: int,
        prompt_path: Path,
        model_resolution: dict,
        blocked_by_usage_limit: bool,
        failure_reason: str | None,
        model_attempts: list[dict],
    ) -> LocalExecutionResult:
        resolved_model = model_resolution.get("resolved_model")
        agent_cli_command = ""
        if resolved_model:
            agent_cli_command = f'claude -p "$(cat platform/system/runtime/local_execution/agent_prompt.md)" --model {resolved_model}'
        return LocalExecutionResult(
            adapter_mode=adapter_mode,
            approval_required=bool(repository.get("approval_required", False)),
            execution_gate=execution_gate,
            agent_cli_command=agent_cli_command,
            request_id=request["request_id"],
            request_status=request["request_status"],
            repository_health=repository.get("repository_health", "unknown"),
            validation_status=repository.get("validation_status", "unknown"),
            worktree_state=repository.get("worktree_state", "unknown"),
            resolved_model=resolved_model,
            model_policy=model_resolution["model_policy"],
            model_resolution_reason=model_resolution["selection_reason"],
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            captured_at=model_resolution["resolved_at"],
            source_artifacts=[
                "platform/system/runtime/supervisor/latest.json",
                "platform/system/runtime/repository_state/latest.json",
                "platform/system/runtime/planning/latest.json",
                "platform/system/runtime/request/execution_request.json",
                "platform/system/runtime/local_execution/model_resolution.json",
                str(prompt_path.relative_to(self.base_path)),
            ],
            blocked_by_usage_limit=blocked_by_usage_limit,
            failure_reason=failure_reason,
            model_attempts=model_attempts,
        )

    def _write_runtime(self, result: LocalExecutionResult) -> None:
        payload = asdict(result)
        for runtime_dir in self._runtime_dirs("local_execution"):
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (runtime_dir / "latest.md").write_text(self._to_markdown(result), encoding="utf-8")

    def _to_markdown(self, result: LocalExecutionResult) -> str:
        return "\n".join(
            [
                "# LOCAL_EXECUTION",
                "",
                f"adapter_mode: {result.adapter_mode}",
                f"approval_required: {str(result.approval_required).lower()}",
                f"execution_gate: {result.execution_gate}",
                f"request_id: {result.request_id}",
                f"request_status: {result.request_status}",
                f"resolved_model: {result.resolved_model or 'null'}",
                f"failure_reason: {result.failure_reason or 'null'}",
                f"exit_code: {result.exit_code}",
                f"model_attempts: {json.dumps(result.model_attempts, ensure_ascii=False)}",
                "",
            ]
        )

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_request(self) -> dict | None:
        for path in self._runtime_paths("request", "execution_request.json"):
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        return None

    def _runtime_dirs(self, *parts: str) -> list[Path]:
        return [self.base_path / "system" / "runtime" / Path(*parts), self.base_path / "runtime" / Path(*parts)]

    def _runtime_path(self, *parts: str) -> Path:
        for path in self._runtime_dirs(*parts):
            if path.exists():
                return path
        return self.base_path / "system" / "runtime" / Path(*parts)

    def _runtime_paths(self, *parts: str) -> list[Path]:
        return self._runtime_dirs(*parts)
