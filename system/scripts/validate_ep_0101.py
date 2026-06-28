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
def main() -> int:
    required_paths = [
        ROOT / "graph" / "repository_graph.json",
        ROOT / "graph" / "repository_graph.md",
        ROOT / "graph" / "agent_context_pack.json",
        ROOT / "system" / "orchestrator" / "context_bundle.json",
        ROOT / "system" / "orchestrator" / "execution_plan.json",
        ROOT / "system" / "runtime" / "task_intake" / "ART-SAMPLE-0001" / "runtime_context.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0101 artifacts:", ", ".join(missing))
        return 1
    import subprocess
    commands = [
        [sys.executable, "system/scripts/agent_runtime/validate_agent_runtime_mvp.py"],
        [sys.executable, "system/scripts/agent_runtime/validate_task_intake.py"],
    ]
    for cmd in commands:
        print("$ " + " ".join(cmd))
        subprocess.check_call(cmd, cwd=ROOT)
    print("EP-0101 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
