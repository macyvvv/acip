#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orchestrator.validation_orchestrator import ValidationOrchestrator


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
