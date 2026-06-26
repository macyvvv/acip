from __future__ import annotations

from dataclasses import asdict, dataclass
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
        command = self._build_command(request, dry_run=dry_run)
        stdout = "dry-run only" if dry_run else self._run_command(command)
        result = LocalExecutionResult(
            adapter_mode="dry_run" if dry_run else "execute",
            approval_required=bool(repository.get("approval_required", False)),
            execution_gate="closed" if dry_run else "open",
            codex_cli_command=command,
            request_id=request["request_id"],
            request_status=request["request_status"],
            repository_health=repository.get("repository_health", "unknown"),
            validation_status=repository.get("validation_status", "unknown"),
            worktree_state=repository.get("worktree_state", "unknown"),
            stdout=stdout,
            stderr="",
            exit_code=0,
            captured_at="deterministic",
            source_artifacts=[
                "runtime/supervisor/latest.json",
                "runtime/repository_state/latest.json",
                "runtime/planning/latest.json",
                "runtime/request/execution_request.json",
            ],
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

    def _build_command(self, request: dict, *, dry_run: bool) -> str:
        suffix = "--dry-run" if dry_run else "--run"
        return f"codex {suffix} --request {request['request_id']}"

    def _run_command(self, command: str) -> str:
        completed = subprocess.run(command, shell=True, capture_output=True, text=True)
        if completed.returncode != 0:
            raise LocalExecutionError(f"Codex command failed: {completed.returncode}")
        return completed.stdout

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
