#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    required = [
        ROOT / "contracts" / "WORKER_EXECUTION_CONTRACT.md",
        ROOT / "workers" / "CODEX_WORKER_PROFILE.md",
        ROOT / "workers" / "CHATGPT_WORKER_PROFILE.md",
        ROOT / "workers" / "README_WORKERS.md",
        ROOT / "orchestrator" / "WORKER_ROUTING.md",
        ROOT / "specs" / "WORKFLOW.md",
    ]
    failures = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    contract = (ROOT / "contracts" / "WORKER_EXECUTION_CONTRACT.md").read_text(encoding="utf-8")
    codex = (ROOT / "workers" / "CODEX_WORKER_PROFILE.md").read_text(encoding="utf-8")
    if "Human Boundary" not in contract:
        failures.append("contracts/WORKER_EXECUTION_CONTRACT.md missing Human Boundary")
    if "explicitly specified repository changes" not in codex:
        failures.append("workers/CODEX_WORKER_PROFILE.md missing explicit specification requirement")
    if "runtime external execution" in codex and "No runtime external execution" not in codex:
        failures.append("workers/CODEX_WORKER_PROFILE.md boundary malformed")
    if failures:
        print("# Worker Contract Validation")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("# Worker Contract Validation")
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
