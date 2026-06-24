#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str

REQUIRED_DIRS = [
    "basis", "adr", "wbs", "docs", "catalog", "registry", "contracts",
    "runbooks", "control", "scripts", ".github", ".github/ISSUE_TEMPLATE", ".github/workflows"
]

CORE_REQUIRED_FILES = [
    "README_REPOSITORY_COMPLETE_PACK.md",
    "README_KNOWLEDGE_FACTORY.md",
    "README_AGENT_OS.md",
    "README_RUNTIME_READINESS.md",
    "README_GOVERNANCE.md",
    "basis/026_autonomy_first_policy.md",
    "basis/037_autonomous_workflow_policy.md",
    "basis/042_execution_contract_policy.md",
    "basis/043_safety_gate_policy.md",
    "basis/046_runtime_readiness_boundary.md",
    "basis/049_secret_boundary_policy.md",
    "basis/050_external_action_policy.md",
    "docs/REPOSITORY_COMPLETE_CHECKLIST.md",
    "docs/RUNTIME_READINESS_CHECKLIST.md",
    "contracts/EXECUTION_CONTRACT_TEMPLATE.md",
    "control/TASK_QUEUE.md",
    "runbooks/RB-0006-emergency-stop.md",
    ".github/workflows/full-governance-check.yml",
]

REQUIRED_TEXT = {
    "basis/026_autonomy_first_policy.md": ["Mission", "Approval", "Emergency Stop"],
    "basis/037_autonomous_workflow_policy.md": ["approval bypass", "Repository overrides conversation"],
    "basis/042_execution_contract_policy.md": ["Current Objective must not change", "Runtime implementation remains out of scope"],
    "basis/043_safety_gate_policy.md": ["Runtime Boundary Gate", "Approval Gate"],
    "basis/046_runtime_readiness_boundary.md": ["Runtime implementation must not begin", "Prohibited Before Runtime Approval"],
    "basis/049_secret_boundary_policy.md": ["Secrets must never be committed", "API keys"],
    "basis/050_external_action_policy.md": ["External actions require explicit approval", "Autonomous external actions are prohibited"],
    "README_REPOSITORY_COMPLETE_PACK.md": ["Repository overrides conversation", "Human handles"],
}

PROHIBITED_KEYWORDS = [
    "auto_post(",
    "publish_to_platform(",
    "run_runtime_agent(",
    "scrape_platform(",
]

SCAN_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".txt"}

def exists_file(path: str) -> CheckResult:
    t = ROOT / path
    return CheckResult(f"required file: {path}", t.is_file(), "exists" if t.is_file() else "missing")

def exists_dir(path: str) -> CheckResult:
    t = ROOT / path
    return CheckResult(f"required dir: {path}", t.is_dir(), "exists" if t.is_dir() else "missing")

def contains(path: str, anchors: list[str]) -> list[CheckResult]:
    t = ROOT / path
    if not t.is_file():
        return [CheckResult(f"required text: {path}", False, "file missing")]
    txt = t.read_text(encoding="utf-8", errors="ignore")
    return [CheckResult(f"required text in {path}: {a}", a in txt, "found" if a in txt else "missing") for a in anchors]

def check_prohibited() -> list[CheckResult]:
    failures = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix not in SCAN_SUFFIXES or ".git" in p.parts:
            continue
        rel = p.relative_to(ROOT).as_posix()
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for kw in PROHIBITED_KEYWORDS:
            if kw in txt:
                failures.append(CheckResult(f"prohibited keyword in {rel}", False, kw))
    return failures or [CheckResult("prohibited keywords", True, "none found")]

def run_checks() -> list[CheckResult]:
    results = []
    results.extend(exists_dir(d) for d in REQUIRED_DIRS)
    results.extend(exists_file(f) for f in CORE_REQUIRED_FILES)
    for path, anchors in REQUIRED_TEXT.items():
        results.extend(contains(path, anchors))
    results.extend(check_prohibited())
    return results

def main() -> int:
    results = run_checks()
    failed = [r for r in results if not r.ok]
    print("# ACIP Complete Repository Validation\n")
    for r in results:
        print(f"[{'PASS' if r.ok else 'FAIL'}] {r.name} - {r.detail}")
    if failed:
        print(f"\nValidation failed: {len(failed)} issue(s).")
        return 1
    print("\nValidation passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
