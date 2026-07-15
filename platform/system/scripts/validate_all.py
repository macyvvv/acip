#!/usr/bin/env python3
from __future__ import annotations

import sys
import importlib.util
from pathlib import Path

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    matches: list[Path] = []
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            matches.append(candidate)
    if matches:
        return matches[-1]
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "system"))

_VALIDATION_ORCHESTRATOR_PATH = ROOT / "system" / "orchestrator" / "validation_orchestrator.py"
_spec = importlib.util.spec_from_file_location("validation_orchestrator", _VALIDATION_ORCHESTRATOR_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Unable to load validation orchestrator from {_VALIDATION_ORCHESTRATOR_PATH}")
_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)
ValidationOrchestrator = _module.ValidationOrchestrator


def main() -> int:
    print("Validation policy: platform/docs/current/VALIDATION_COMMAND_POLICY.md")
    orchestrator = ValidationOrchestrator(ROOT)
    result = orchestrator.run()
    for step in result.validation_steps:
        print(f"$ {step.command}")
        if step.output:
            print(step.output, end="" if step.output.endswith("\n") else "\n")
    if result.pytest_result is not None:
        print(f"$ {result.pytest_result.command}")
        if result.pytest_result.output:
            print(result.pytest_result.output, end="" if result.pytest_result.output.endswith("\n") else "\n")
    return 0 if result.overall_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
