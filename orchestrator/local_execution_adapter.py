from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import os
import subprocess
from datetime import datetime, timezone


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
    resolved_model: str
    model_policy: str
    model_resolution_reason: str
    stdout: str
    stderr: str
    exit_code: int
    captured_at: str
    source_artifacts: list[str]


class LocalExecutionError(ValueError):
    pass


class LocalExecutionAdapter:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(self, *, approval_flag: bool = False, dry_run: bool = True) -> LocalExecutionResult:
        supervisor = self._read_json(self.base_path / "runtime" / "supervisor" / "latest.json")
        planning = self._read_json(self.base_path / "runtime" / "planning" / "latest.json")
        repository = self._read_json(self.base_path / "runtime" / "repository_state" / "latest.json")
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
        except Exception as exc:
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
            "dependency": ["runtime/supervisor/latest.json"],
            "worker_assignment": "Codex",
        }

    def _validate_alignment(self, planning: dict, request: dict) -> None:
        objective = planning.get("current_objective", "")
        if not objective:
            raise LocalExecutionError("Missing current objective")
        if request.get("request_status") not in {"ready", "pending_approval"}:
            raise LocalExecutionError("Invalid request status")

    def _render_prompt(self, request: dict, planning: dict, repository: dict) -> str:
        lines = [
            "# Codex Execution Prompt",
            "",
            f"Request ID: {request['request_id']}",
            f"Request Status: {request['request_status']}",
            f"Objective: {planning.get('current_objective', 'unknown')}",
            f"Selected Work Item: {request.get('next_action', 'unknown')}",
            "",
            "Implement Issue #28 / ACCEPTANCE-0001 using repository artifacts only.",
            "Read runtime/planning/latest.json, runtime/repository_state/latest.json, runtime/work_planner/latest.json, and runtime/request/execution_request.json.",
            "Run:",
            "- python3 scripts/validate_all.py",
            "- python3 -m pytest -q",
            "- git status",
            "",
            "Do not auto-push.",
            "Do not modify Repository OS architecture.",
        ]
        return "\n".join(lines) + "\n"

    def _write_prompt(self, prompt: str) -> Path:
        runtime_dir = self.base_path / "runtime" / "local_execution"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = runtime_dir / "codex_prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        return prompt_path

    def _resolve_model(self, request: dict, planning: dict, repository: dict) -> dict:
        policy = os.environ.get("CODEX_MODEL_POLICY", "cost_optimized")
        override = os.environ.get("CODEX_MODEL_OVERRIDE", "").strip()
        supported = self._supported_models()
        required_capability = self._required_capability(request, planning, repository)
        candidate_models = self._rank_models(supported, required_capability, policy)
        if override:
            if override not in supported:
                raise LocalExecutionError(f"Unsupported model override: {override}")
            return {
                "model_policy": policy,
                "resolved_model": override,
                "candidate_models": candidate_models or [override],
                "selection_reason": "local override",
                "fallback_used": bool(candidate_models and override != candidate_models[0]),
                "estimated_cost_tier": self._cost_tier(override),
                "resolved_at": self._resolved_at(),
            }
        if not candidate_models:
            raise LocalExecutionError(
                f"Model resolution failed: no compatible models for capability={required_capability} under policy={policy}"
            )
        resolved_model = candidate_models[0]
        return {
            "model_policy": policy,
            "resolved_model": resolved_model,
            "candidate_models": candidate_models,
            "selection_reason": f"capability={required_capability}; policy={policy}",
            "fallback_used": False,
            "estimated_cost_tier": self._cost_tier(resolved_model),
            "resolved_at": self._resolved_at(),
        }

    def _supported_models(self) -> list[str]:
        configured = os.environ.get("CODEX_SUPPORTED_MODELS", "").strip()
        if configured:
            return [model.strip() for model in configured.split(",") if model.strip()]
        return ["gpt-5.4-mini", "gpt-5.4", "gpt-5.2-mini"]

    def _required_capability(self, request: dict, planning: dict, repository: dict) -> str:
        request_text = " ".join(str(request.get(key, "")) for key in ("request_id", "request_status", "next_action"))
        planning_text = " ".join(str(planning.get(key, "")) for key in ("current_objective", "current_pack", "current_ep"))
        if any(keyword in request_text.lower() or keyword in planning_text.lower() for keyword in ("architecture", "high-risk", "high risk", "approval")):
            return "high_reasoning"
        if repository.get("approval_required"):
            return "reasoning"
        return "cost_optimized"

    def _rank_models(self, supported: list[str], required_capability: str, policy: str) -> list[str]:
        cost_order = {
            "gpt-5.2-mini": 0,
            "gpt-5.4-mini": 1,
            "gpt-5.2": 2,
            "gpt-5.4": 3,
        }
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

    def _run_command(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, capture_output=True, text=True)

    def _write_model_resolution(self, model_resolution: dict) -> None:
        runtime_dir = self.base_path / "runtime" / "local_execution"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            **model_resolution,
            "supported_models": self._supported_models(),
            "source_artifacts": [
                "runtime/supervisor/latest.json",
                "runtime/repository_state/latest.json",
                "runtime/planning/latest.json",
                "runtime/request/execution_request.json",
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
    ) -> LocalExecutionResult:
        return LocalExecutionResult(
            adapter_mode=adapter_mode,
            approval_required=bool(repository.get("approval_required", False)),
            execution_gate=execution_gate,
            codex_cli_command=f"codex exec -m {model_resolution['resolved_model']} \"$(cat runtime/local_execution/codex_prompt.md)\"",
            request_id=request["request_id"],
            request_status=request["request_status"],
            repository_health=repository.get("repository_health", "unknown"),
            validation_status=repository.get("validation_status", "unknown"),
            worktree_state=repository.get("worktree_state", "unknown"),
            resolved_model=model_resolution["resolved_model"],
            model_policy=model_resolution["model_policy"],
            model_resolution_reason=model_resolution["selection_reason"],
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            captured_at=model_resolution["resolved_at"],
            source_artifacts=[
                "runtime/supervisor/latest.json",
                "runtime/repository_state/latest.json",
                "runtime/planning/latest.json",
                "runtime/request/execution_request.json",
                "runtime/local_execution/model_resolution.json",
                str(prompt_path.relative_to(self.base_path)),
            ],
        )

    def _write_runtime(self, result: LocalExecutionResult) -> None:
        runtime_dir = self.base_path / "runtime" / "local_execution"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(result)
        (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (runtime_dir / "latest.md").write_text(self._to_markdown(result), encoding="utf-8")

    def _to_markdown(self, result: LocalExecutionResult) -> str:
        return "\n".join([
            "# LOCAL_EXECUTION",
            "",
            f"adapter_mode: {result.adapter_mode}",
            f"approval_required: {str(result.approval_required).lower()}",
            f"execution_gate: {result.execution_gate}",
            f"request_id: {result.request_id}",
            f"request_status: {result.request_status}",
            f"exit_code: {result.exit_code}",
            "",
        ])

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_request(self) -> dict | None:
        path = self.base_path / "runtime" / "request" / "execution_request.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
