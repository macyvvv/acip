from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import re
import subprocess
import sys
from typing import Iterable

from system.core.path_resolver import get_repo_root


EP_PATTERN = re.compile(r"^validate_ep_(\d{4})\.py$")


@dataclass(frozen=True)
class ValidationStepResult:
    command: str
    exit_code: int
    success: bool
    output: str = ""


@dataclass(frozen=True)
class ValidationOrchestrationResult:
    validation_steps: list[ValidationStepResult] = field(default_factory=list)
    pytest_result: ValidationStepResult | None = None
    overall_success: bool = False
    validation_owner: str = "Codex"
    rerun_required_when: tuple[str, ...] = (
        "any validation step fails",
        "pytest fails",
        "runtime validation report is stale",
        "validation state does not match repository outputs",
    )
    human_rerun_policy: str = (
        "Human reruns validation only when repository outputs changed, validation artifacts are stale, "
        "or the latest validation failed."
    )
    relation_to_worker_output_contract: str = (
        "Validation state is a repository-level summary of validation execution and is referenced by "
        "Worker Output Contract as the canonical validation status for review and handoff."
    )


class ValidationOrchestratorError(RuntimeError):
    pass


class ValidationOrchestrator:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root) if root != "." else get_repo_root()

    def discover_validation_scripts(self) -> list[Path]:
        scripts_dir = self.root / "system" / "scripts"
        if not scripts_dir.exists():
            scripts_dir = self.root / "scripts"
        discovered = []
        for path in scripts_dir.glob("validate_ep_*.py"):
            if EP_PATTERN.match(path.name):
                discovered.append(path)
        return sorted(discovered, key=lambda path: path.name)

    def run(self) -> ValidationOrchestrationResult:
        steps: list[ValidationStepResult] = []
        for script_path in self.discover_validation_scripts():
            command = [sys.executable, str(script_path.relative_to(self.root))]
            result = self._run_command(command)
            steps.append(result)
            if not result.success:
                return ValidationOrchestrationResult(validation_steps=steps, pytest_result=None, overall_success=False)

        pytest_result = self._run_command(self._resolve_pytest_command())
        steps.append(pytest_result)
        overall_success = pytest_result.success and all(step.success for step in steps)
        return ValidationOrchestrationResult(validation_steps=steps[:-1], pytest_result=pytest_result, overall_success=overall_success)

    def build_report(self, result: ValidationOrchestrationResult) -> tuple[str, str]:
        payload = {
            "validation_steps": [
                {
                    "command": step.command,
                    "exit_code": step.exit_code,
                    "success": step.success,
                }
                for step in result.validation_steps
            ],
            "pytest": None
            if result.pytest_result is None
            else {
                "command": result.pytest_result.command,
                "exit_code": result.pytest_result.exit_code,
                "success": result.pytest_result.success,
            },
            "overall_success": result.overall_success,
            "validation_owner": result.validation_owner,
            "rerun_required_when": list(result.rerun_required_when),
            "human_rerun_policy": result.human_rerun_policy,
            "relation_to_worker_output_contract": result.relation_to_worker_output_contract,
        }
        json_report = json.dumps(payload, ensure_ascii=False, indent=2)

        lines = ["# VALIDATION REPORT", ""]
        for step in result.validation_steps:
            status = "PASS" if step.success else "FAIL"
            lines.append(f"- {status} `{step.command}` (exit {step.exit_code})")
        if result.pytest_result is not None:
            status = "PASS" if result.pytest_result.success else "FAIL"
            lines.append(f"- {status} `{result.pytest_result.command}` (exit {result.pytest_result.exit_code})")
        lines.append("")
        lines.append(f"overall_success: {str(result.overall_success).lower()}")
        markdown_report = "\n".join(lines) + "\n"
        return json_report, markdown_report

    def write_reports(self, result: ValidationOrchestrationResult) -> None:
        runtime_dir = self.root / "system" / "runtime" / "validation"
        if not runtime_dir.parent.parent.exists():
            runtime_dir = self.root / "runtime" / "validation"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        json_report, markdown_report = self.build_report(result)
        (runtime_dir / "validation_report.json").write_text(json_report, encoding="utf-8")
        (runtime_dir / "VALIDATION_REPORT.md").write_text(markdown_report, encoding="utf-8")

        validation_state = self.root / "docs" / "current" / "VALIDATION_STATE.md"
        validation_state.parent.mkdir(parents=True, exist_ok=True)
        validation_state.write_text(
            "\n".join(
                [
                    "# VALIDATION_STATE",
                    "",
                    f"last_validation_status: {'success' if result.overall_success else 'failure'}",
                    f"last_validation_command: python3 system/scripts/validate_all.py",
                    f"last_validation_report_json: system/runtime/validation/validation_report.json",
                    f"last_validation_report_md: system/runtime/validation/VALIDATION_REPORT.md",
                    f"validation_owner: {result.validation_owner}",
                    "rerun_required_when:",
                    *[f"  - {item}" for item in result.rerun_required_when],
                    f"human_rerun_policy: {result.human_rerun_policy}",
                    f"relation_to_worker_output_contract: {result.relation_to_worker_output_contract}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _run_command(self, command: list[str]) -> ValidationStepResult:
        completed = subprocess.run(
            command,
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        output = (completed.stdout or "") + (completed.stderr or "")
        return ValidationStepResult(
            command=" ".join(command),
            exit_code=completed.returncode,
            success=completed.returncode == 0,
            output=output,
        )

    def _resolve_pytest_command(self) -> list[str]:
        if self._interpreter_has_pytest(sys.executable):
            return [sys.executable, "-m", "pytest", "-q"]

        known_good = Path("/Library/Developer/CommandLineTools/usr/bin/python3")
        if known_good.exists():
            return [str(known_good), "-m", "pytest", "-q"]

        return [sys.executable, "-m", "pytest", "-q"]

    def _interpreter_has_pytest(self, interpreter: str) -> bool:
        probe = subprocess.run(
            [
                interpreter,
                "-c",
                "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('pytest') else 1)",
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        return probe.returncode == 0
