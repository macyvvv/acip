from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess

from system.core.agent_role_registry import get_role
from system.core.business_registry import get_business
from system.core.kpi_store import update_business_agent_kpi
from system.scripts.analytics.providers import get_provider as get_analytics_provider

# Sibling to platform/system/orchestrator/local_execution_adapter.py, not a modification of
# it: that adapter's safety checks/deliverable verification are tied to
# GitHub-issue-shaped repo-dev work (supervisor/planning/repository_state
# projections, a hardcoded per-issue deliverable checklist) which has no
# equivalent for a business-agent role invocation. The small slice of model-
# resolution logic below is deliberately duplicated, not extracted, until a
# second real claude_invocation consumer exists (see ADR-0032 for why this
# codebase treats premature shared abstractions as a real risk, not a nicety).
DEFAULT_SUPPORTED_MODELS = ["claude-haiku-4-5", "claude-sonnet-5", "claude-opus-4-8"]
DEFAULT_CLI_TIMEOUT_SECONDS = 60

# A headless `claude -p ... --tools ... --permission-mode bypassPermissions`
# call can exit 0 while printing only an account-level usage/session-limit
# notice instead of doing any real work -- observed live via Level 3b's first
# real scheduled wake (ADR-0038): 3 scopes were recorded execution_result_
# status=success with exit_code=0, but their only stdout was a session-limit
# notice, and no real content was produced. Exit code alone is not a
# sufficient success signal for headless automation here, the same lesson
# already learned once for --allowedTools not being a hard restriction --
# the CLI's own signals need independent verification, not blind trust.
_CLI_FAILURE_NOTICE_PATTERNS = ("session limit", "rate limit", "usage limit")
# These notices are short, single-line messages, not real generated content --
# bounding the check by length keeps it from false-positiving on legitimate
# long-form content that happens to discuss rate limits as a topic.
_CLI_FAILURE_NOTICE_MAX_LEN = 500


def _cli_failure_notice(stdout: str) -> str | None:
    """Returns a short reason string if stdout looks like a CLI-level failure
    notice rather than real content, else None."""
    text = stdout.strip()
    if not text:
        return "empty_stdout"
    if len(text) <= _CLI_FAILURE_NOTICE_MAX_LEN:
        lowered = text.lower()
        for pattern in _CLI_FAILURE_NOTICE_PATTERNS:
            if pattern in lowered:
                return f"cli_notice:{pattern.replace(' ', '_')}"
    return None


@dataclass(frozen=True)
class BusinessAgentExecutionResult:
    business_id: str
    role_id: str
    task_id: str
    adapter_mode: str
    resolved_model: str | None
    model_capability: str
    allowed_tools: list[str]
    agent_cli_command: str
    stdout: str
    stderr: str
    exit_code: int
    success: bool
    captured_at: str
    artifact_path: str
    failure_reason: str | None = None


class BusinessAgentExecutionError(ValueError):
    pass


class BusinessAgentExecutionAdapter:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def run(
        self,
        *,
        business_id: str,
        role_id: str,
        task_id: str,
        task_description: str = "",
        approval_flag: bool = False,
        dry_run: bool = True,
    ) -> BusinessAgentExecutionResult:
        business = get_business(business_id, self.base_path)
        if business is None:
            raise BusinessAgentExecutionError(f"Unknown business_id: {business_id}")
        role = get_role(role_id, self.base_path)
        if role is None:
            raise BusinessAgentExecutionError(f"Unknown role_id: {role_id}")
        if role.role_kind == "pluggable_provider":
            raise BusinessAgentExecutionError(
                f"role_kind={role.role_kind} execution is not wired yet (Stage 4 work); "
                f"only claude_invocation and data_fetch roles run today"
            )
        if not dry_run and not approval_flag:
            raise BusinessAgentExecutionError("Real execution requires explicit approval flag")

        if role.role_kind == "data_fetch":
            return self._run_data_fetch(business_id, role, task_id, dry_run)

        prompt = self._render_prompt(business, role, task_description)
        model = self._resolve_model(role.model_capability)
        command = self._build_command(prompt, model, role.allowed_tools)
        agent_cli_command = " ".join([command[0], command[1], '"<rendered prompt>"'] + command[3:])

        adapter_mode = "dry_run" if dry_run else "execute"
        stdout = "dry-run only"
        stderr = ""
        exit_code = 0
        if not dry_run:
            completed = self._run_command(command)
            stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode

        # Only applied to a real (non-dry-run) call -- dry_run's fixed
        # "dry-run only" stdout never matches a failure-notice pattern, so
        # this is a no-op for dry runs, not a special case.
        failure_reason = _cli_failure_notice(stdout) if not dry_run else None
        success = exit_code == 0 and failure_reason is None
        result = BusinessAgentExecutionResult(
            business_id=business_id,
            role_id=role_id,
            task_id=task_id,
            adapter_mode=adapter_mode,
            resolved_model=model,
            model_capability=role.model_capability,
            allowed_tools=list(role.allowed_tools),
            agent_cli_command=agent_cli_command,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            success=success,
            captured_at=datetime.now(timezone.utc).isoformat(),
            artifact_path=str(self._artifact_dir(business_id, role_id, task_id) / "latest.json"),
            failure_reason=failure_reason,
        )
        self._write_artifact(result)
        update_business_agent_kpi(business_id, role_id, success, self.base_path)
        return result

    def _run_data_fetch(self, business_id: str, role, task_id: str, dry_run: bool) -> BusinessAgentExecutionResult:
        adapter_mode = "dry_run" if dry_run else "execute"
        if dry_run:
            stdout = "dry-run only"
            metrics: dict[str, float] = {}
        else:
            provider = get_analytics_provider(role.default_provider)
            fetch_result = provider.fetch(business_id)
            stdout = fetch_result.notes
            metrics = fetch_result.metrics

        success = True
        result = BusinessAgentExecutionResult(
            business_id=business_id,
            role_id=role.role_id,
            task_id=task_id,
            adapter_mode=adapter_mode,
            resolved_model=None,
            model_capability=role.model_capability,
            allowed_tools=list(role.allowed_tools),
            agent_cli_command=f"analytics provider={role.default_provider}",
            stdout=stdout,
            stderr="",
            exit_code=0,
            success=success,
            captured_at=datetime.now(timezone.utc).isoformat(),
            artifact_path=str(self._artifact_dir(business_id, role.role_id, task_id) / "latest.json"),
        )
        self._write_artifact(result)
        update_business_agent_kpi(business_id, role.role_id, success, self.base_path, metrics=metrics or None)
        return result

    def _render_prompt(self, business, role, task_description: str) -> str:
        template = (self.base_path / role.prompt_template_path).read_text(encoding="utf-8")
        business_context = business.notes
        return (
            template.replace("{business_name}", business.display_name)
            .replace("{business_context}", business_context)
            .replace("{task}", task_description or "(no task description provided)")
        )

    def _resolve_model(self, model_capability: str) -> str:
        capability_floor = {"cost_optimized": 0, "reasoning": 1, "high_reasoning": 2}
        floor = capability_floor.get(model_capability, 0)
        candidates = [model for model in DEFAULT_SUPPORTED_MODELS if self._model_cost_rank(model) >= floor]
        reverse = model_capability == "high_reasoning"
        candidates.sort(key=lambda model: (self._model_cost_rank(model), model), reverse=reverse)
        if not candidates:
            raise BusinessAgentExecutionError(f"No supported model meets capability={model_capability}")
        return candidates[0]

    def _model_cost_rank(self, model: str) -> int:
        order = {"claude-haiku-4-5": 0, "claude-sonnet-5": 1, "claude-opus-4-8": 2}
        return order.get(model, 1)

    def _build_command(self, prompt: str, model: str, allowed_tools: tuple[str, ...] | list[str]) -> list[str]:
        # --allowedTools only skips permission *prompts* for named tools; it does not
        # cap what's available. --tools is the actual hard restriction (defines the
        # available toolset outright), so it -- not --allowedTools -- is what makes
        # this role meaningfully less trusted than the full-access repo-dev path.
        # --permission-mode bypassPermissions is safe here specifically because
        # --tools has already capped the surface to read-only tools per role.
        return [
            "claude",
            "-p",
            prompt,
            "--model",
            model,
            "--tools",
            ",".join(allowed_tools),
            "--permission-mode",
            "bypassPermissions",
        ]

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

    def _artifact_dir(self, business_id: str, role_id: str, task_id: str) -> Path:
        return self.base_path / "system" / "runtime" / "business_agents" / business_id / role_id / task_id

    def _write_artifact(self, result: BusinessAgentExecutionResult) -> None:
        artifact_dir = self._artifact_dir(result.business_id, result.role_id, result.task_id)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(result)
        (artifact_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (artifact_dir / "latest.md").write_text(self._to_markdown(result), encoding="utf-8")

    def _to_markdown(self, result: BusinessAgentExecutionResult) -> str:
        return "\n".join(
            [
                "# BUSINESS_AGENT_EXECUTION",
                "",
                f"business_id: {result.business_id}",
                f"role_id: {result.role_id}",
                f"task_id: {result.task_id}",
                f"adapter_mode: {result.adapter_mode}",
                f"resolved_model: {result.resolved_model or 'null'}",
                f"success: {str(result.success).lower()}",
                f"exit_code: {result.exit_code}",
                "",
                "## stdout",
                result.stdout,
                "",
            ]
        )
