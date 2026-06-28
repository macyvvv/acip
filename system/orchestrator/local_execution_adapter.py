from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess


@dataclass(frozen=True)
class LocalExecutionResult:
    adapter_mode: str
    approval_required: bool
    execution_gate: str
    codex_cli_command: str
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

        if not supervisor:
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
            failure_reason = str(model_resolution.get("failure_reason", "unsupported_model_for_auth_mode"))
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
        try:
            if not dry_run:
                completed = self._run_command(command)
                stdout = completed.stdout
                stderr = completed.stderr
                exit_code = completed.returncode
                if exit_code != 0:
                    raise LocalExecutionError(f"Codex command failed: {exit_code}")
                deliverable_check = self._verify_deliverables(request)
                if not deliverable_check["ok"]:
                    raise LocalExecutionError("missing_deliverables")
        except Exception as exc:
            blocked_by_usage_limit = self._is_usage_limit_error(exc) or self._is_usage_limit_error(stderr)
            failure_reason = "blocked_by_usage_limit" if blocked_by_usage_limit else str(exc)
            if failure_reason == "missing_deliverables":
                blocked_by_usage_limit = False
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
            )
            self._write_runtime(result)
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
        )
        self._write_runtime(result)
        return result

    def _derive_request(self, supervisor: dict) -> dict:
        payload = supervisor.get("codex_intake_payload", {})
        return {
            "request_id": f"REQ-{payload.get('current_ep', 'UNKNOWN')}",
            "request_status": "ready",
            "request_priority": 0,
            "approval_required": False,
            "dependency": ["system/runtime/supervisor/latest.json"],
            "worker_assignment": "Codex",
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
            "# Codex Execution Prompt",
            "",
            f"Request ID: {request['request_id']}",
            f"Request Status: {request['request_status']}",
            f"Objective: {objective}",
            f"Selected Work Item: {request.get('next_action', 'unknown')}",
            f"Selected Issue Number: {request.get('issue_number', 'unknown')}",
            f"Selected Issue Title: {request.get('issue_title', 'unknown')}",
            "",
            issue_instruction,
            "Read system/runtime/planning/latest.json, system/runtime/repository_state/latest.json, system/runtime/work_planner/latest.json, and system/runtime/request/execution_request.json.",
            "Run:",
            "- python3 system/scripts/validate_all.py",
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
        prompt_path = runtime_dir / "codex_prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        return prompt_path

    def _resolve_model(self, request: dict, planning: dict, repository: dict) -> dict:
        policy = os.environ.get("CODEX_MODEL_POLICY", "cost_optimized")
        override = os.environ.get("CODEX_MODEL_OVERRIDE", "").strip()
        auth_mode = self._auth_mode()
        configured_models = self._supported_models()
        candidate_models = self._rank_models(configured_models, request, planning, repository, policy)
        supported_models, rejected_models = self._filter_supported_models(candidate_models, auth_mode)

        if override:
            if override not in configured_models:
                raise LocalExecutionError(f"Unsupported model override: {override}")
            if override not in supported_models:
                return self._failed_model_resolution(
                    auth_mode=auth_mode,
                    policy=policy,
                    candidate_models=candidate_models,
                    rejected_models=rejected_models,
                    reason="unsupported_model_for_auth_mode",
                )
            return self._resolved_model_resolution(
                auth_mode=auth_mode,
                policy=policy,
                candidate_models=candidate_models,
                rejected_models=rejected_models,
                resolved_model=override,
                selection_reason="local override",
            )

        if not supported_models:
            return self._failed_model_resolution(
                auth_mode=auth_mode,
                policy=policy,
                candidate_models=candidate_models,
                rejected_models=rejected_models,
                reason="unsupported_model_for_auth_mode",
            )

        resolved_model = supported_models[0]
        selection_reason = f"capability={self._required_capability(request, planning, repository)}; policy={policy}"
        return self._resolved_model_resolution(
            auth_mode=auth_mode,
            policy=policy,
            candidate_models=candidate_models,
            rejected_models=rejected_models,
            resolved_model=resolved_model,
            selection_reason=selection_reason,
            fallback_used=resolved_model != candidate_models[0] if candidate_models else False,
        )

    def _failed_model_resolution(
        self,
        *,
        auth_mode: str,
        policy: str,
        candidate_models: list[str],
        rejected_models: list[dict],
        reason: str,
    ) -> dict:
        return {
            "auth_mode": auth_mode,
            "model_policy": policy,
            "candidate_models": candidate_models,
            "rejected_models": rejected_models,
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
        auth_mode: str,
        policy: str,
        candidate_models: list[str],
        rejected_models: list[dict],
        resolved_model: str,
        selection_reason: str,
        fallback_used: bool = False,
    ) -> dict:
        supported_models = [model for model in candidate_models if model not in {entry["model"] for entry in rejected_models}]
        return {
            "auth_mode": auth_mode,
            "model_policy": policy,
            "candidate_models": candidate_models,
            "rejected_models": rejected_models,
            "supported_models": supported_models,
            "resolved_model": resolved_model,
            "fallback_used": fallback_used,
            "estimated_cost_tier": self._cost_tier(resolved_model),
            "selection_reason": selection_reason,
            "resolved_at": self._resolved_at(),
            "failure_reason": None,
        }

    def _supported_models(self) -> list[str]:
        configured = os.environ.get("CODEX_SUPPORTED_MODELS", "").strip()
        if configured:
            return [model.strip() for model in configured.split(",") if model.strip()]
        return ["gpt-5.4-mini", "gpt-5.4", "gpt-5.2-mini"]

    def _auth_mode(self) -> str:
        return os.environ.get("CODEX_AUTH_MODE", "chatgpt").strip().lower() or "chatgpt"

    def _required_capability(self, request: dict, planning: dict, repository: dict) -> str:
        request_text = " ".join(str(request.get(key, "")) for key in ("request_id", "request_status", "next_action"))
        planning_text = " ".join(str(planning.get(key, "")) for key in ("current_objective", "current_pack", "current_ep"))
        if any(keyword in request_text.lower() or keyword in planning_text.lower() for keyword in ("architecture", "high-risk", "high risk", "approval")):
            return "high_reasoning"
        if repository.get("approval_required"):
            return "reasoning"
        return "cost_optimized"

    def _rank_models(self, supported: list[str], request: dict, planning: dict, repository: dict, policy: str) -> list[str]:
        cost_order = {
            "gpt-5.2-mini": 0,
            "gpt-5.4-mini": 1,
            "gpt-5.2": 2,
            "gpt-5.4": 3,
        }
        required_capability = self._required_capability(request, planning, repository)
        capability_floor = {
            "cost_optimized": {"gpt-5.2-mini", "gpt-5.4-mini", "gpt-5.2", "gpt-5.4"},
            "reasoning": {"gpt-5.4-mini", "gpt-5.2", "gpt-5.4"},
            "high_reasoning": {"gpt-5.4", "gpt-5.2", "gpt-5.4-mini"},
        }
        allowed = capability_floor.get(required_capability, set(supported))
        candidates = [model for model in supported if model in allowed]
        if policy == "high_reasoning":
            candidates = [model for model in candidates if model in {"gpt-5.4", "gpt-5.2", "gpt-5.4-mini"}]
        candidates.sort(key=lambda model: (cost_order.get(model, 99), model))
        return candidates

    def _filter_supported_models(self, candidate_models: list[str], auth_mode: str) -> tuple[list[str], list[dict]]:
        auth_allowlist = {
            "chatgpt": {"gpt-5.4-mini", "gpt-5.4"},
            "api": {"gpt-5.2-mini", "gpt-5.4-mini", "gpt-5.2", "gpt-5.4"},
        }
        allowed = auth_allowlist.get(auth_mode, auth_allowlist["chatgpt"])
        supported_models = [model for model in candidate_models if model in allowed]
        rejected_models = [{"model": model, "reason": f"unsupported_for_auth_mode:{auth_mode}"} for model in candidate_models if model not in allowed]
        return supported_models, rejected_models

    def _cost_tier(self, model: str) -> str:
        if model == "gpt-5.2-mini":
            return "lowest"
        if model == "gpt-5.4-mini":
            return "low"
        if model == "gpt-5.2":
            return "medium"
        return "high"

    def _resolved_at(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _build_command(self, prompt_path: Path, model: str) -> list[str]:
        return ["codex", "exec", "-m", model, prompt_path.read_text(encoding="utf-8")]

    def _is_usage_limit_error(self, value: object) -> bool:
        text = str(value).lower()
        return "usage limit" in text or "out of credits" in text

    def _verify_deliverables(self, request: dict) -> dict:
        issue_number = request.get("issue_number")
        issue_title = str(request.get("issue_title", "")).upper()
        required_paths_by_issue = {
            30: [
                "product/minimal_launch_brief_generator/README.md",
                "product/minimal_launch_brief_generator/requirements.md",
                "product/minimal_launch_brief_generator/architecture.md",
                "product/minimal_launch_brief_generator/release_notes.md",
                "product/minimal_launch_brief_generator/src/__init__.py",
                "product/minimal_launch_brief_generator/src/minimal_launch_brief_generator.py",
                "product/minimal_launch_brief_generator/tests/test_minimal_launch_brief_generator.py",
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
        return subprocess.run(command, capture_output=True, text=True)

    def _write_model_resolution(self, model_resolution: dict) -> None:
        runtime_dir = self._runtime_path("local_execution")
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            **model_resolution,
            "source_artifacts": [
                "system/runtime/supervisor/latest.json",
                "system/runtime/repository_state/latest.json",
                "system/runtime/planning/latest.json",
                "system/runtime/request/execution_request.json",
            ],
        }
        (runtime_dir / "model_resolution.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

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
    ) -> LocalExecutionResult:
        resolved_model = model_resolution.get("resolved_model")
        codex_cli_command = ""
        if resolved_model:
            codex_cli_command = f'codex exec -m {resolved_model} "$(cat system/runtime/local_execution/codex_prompt.md)"'
        return LocalExecutionResult(
            adapter_mode=adapter_mode,
            approval_required=bool(repository.get("approval_required", False)),
            execution_gate=execution_gate,
            codex_cli_command=codex_cli_command,
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
                "system/runtime/supervisor/latest.json",
                "system/runtime/repository_state/latest.json",
                "system/runtime/planning/latest.json",
                "system/runtime/request/execution_request.json",
                "system/runtime/local_execution/model_resolution.json",
                str(prompt_path.relative_to(self.base_path)),
            ],
            blocked_by_usage_limit=blocked_by_usage_limit,
            failure_reason=failure_reason,
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
