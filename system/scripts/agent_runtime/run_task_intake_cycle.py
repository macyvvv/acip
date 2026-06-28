#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_runtime.task_cycle import run_task_intake_cycle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="system/runtime/task_inputs/sample_task.json")
    args = parser.parse_args()
    result = run_task_intake_cycle(Path(args.task), ROOT)
    print("# Agent Runtime Task Intake Dry Run")
    print(f"status={result['status']}")
    print(f"task_id={result['task_id']}")
    print(f"output_dir={result['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
