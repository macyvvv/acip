#!/usr/bin/env python3
from pathlib import Path
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
REQUIRED = [
    "VERSION",
    "platform/releases/RELEASE_v1.0.0-repository-os.md",
    "platform/baseline/BASELINE_MANIFEST.md",
    "platform/baseline/BASELINE_CHANGE_POLICY.md",
    # platform/basis/077-081 were confirmed-empty stub placeholders (never authored)
    # and were archived by the 2026-07 governance overhaul (platform/adr/ADR-0037)
    # along with the rest of platform/basis/'s non-load-bearing corpus.
    "archive/basis_corpus_2026/077_baseline_policy.md",
    "archive/basis_corpus_2026/078_incremental_graph_policy.md",
    "archive/basis_corpus_2026/079_context_diff_policy.md",
    "archive/basis_corpus_2026/080_execution_queue_automation_policy.md",
    "archive/basis_corpus_2026/081_review_gate_summary_policy.md",
    "platform/adr/ADR-0024-repository-os-v1-baseline.md",
    "platform/adr/ADR-0025-incremental-graph-and-context-diff.md",
    "platform/wbs/WBS-0016-repository-os-v1-baseline.md",
]

def main() -> int:
    failures = [p for p in REQUIRED if not (ROOT / p).exists()]
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else ""
    if version != "1.0.0-repository-os":
        failures.append("VERSION must be 1.0.0-repository-os")
    if failures:
        print("# Baseline Validation")
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print("# Baseline Validation")
    print("Validation passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
