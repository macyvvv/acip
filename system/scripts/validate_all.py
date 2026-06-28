#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

from system.orchestrator.validation_orchestrator import ValidationOrchestrator


def main() -> int:
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
