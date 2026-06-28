#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
REQUIRED_FILES = [
    "system/orchestrator/AGENT_ROUTER.md",
    "system/orchestrator/CONTEXT_RESOLVER.md",
    "system/orchestrator/EXECUTION_QUEUE.md",
    "system/orchestrator/REVIEW_GATE.md",
    "system/orchestrator/ORCHESTRATION_SEQUENCE.md",
    "system/orchestrator/CONTEXT_BUNDLE_SCHEMA.md",
    "system/orchestrator/EXECUTION_PLAN_SCHEMA.md",
    "basis/072_agent_orchestrator_policy.md",
    "basis/073_task_router_policy.md",
    "basis/074_context_resolution_policy.md",
    "basis/075_execution_queue_policy.md",
    "basis/076_review_gate_policy.md",
    "adr/ADR-0022-agent-orchestrator.md",
    "adr/ADR-0023-task-routing.md",
    "wbs/WBS-0015-agent-orchestrator.md",
    "graph/repository_graph.json",
    "graph/agent_context_pack.json",
]

PROHIBITED = [
    "auto_post(",
    "publish_to_platform(",
    "run_runtime_agent(",
    "scrape_platform(",
]

def ensure_generated() -> None:
    if not (ROOT / "orchestrator" / "context_bundle.json").exists():
        subprocess.check_call([sys.executable, "system/scripts/system/orchestrator/build_context_bundle.py"], cwd=ROOT)
    if not (ROOT / "orchestrator" / "execution_plan.json").exists():
        subprocess.check_call([sys.executable, "system/scripts/system/orchestrator/build_execution_plan.py"], cwd=ROOT)

def main() -> int:
    ensure_generated()
    failures = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")

    for rel in ["system/orchestrator/context_bundle.json", "system/orchestrator/execution_plan.json"]:
        if not (ROOT / rel).exists():
            failures.append(f"missing generated file: {rel}")

    if (ROOT / "orchestrator" / "execution_plan.json").exists():
        plan = json.loads((ROOT / "orchestrator" / "execution_plan.json").read_text(encoding="utf-8"))
        prohibited = set(plan.get("prohibited_actions", []))
        required = {"runtime agent execution", "auto posting", "platform API mutation", "secret use", "approval bypass"}
        missing = required - prohibited
        if missing:
            failures.append(f"execution plan missing prohibited actions: {sorted(missing)}")

    for path in (ROOT / "orchestrator").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".py"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for keyword in PROHIBITED:
                if keyword in text:
                    failures.append(f"prohibited operational keyword in {path.relative_to(ROOT)}: {keyword}")

    if failures:
        print("# Agent Orchestrator Validation")
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print("# Agent Orchestrator Validation")
    print("Validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
