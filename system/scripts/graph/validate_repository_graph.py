#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
GRAPH = ROOT / "graph" / "repository_graph.json"

def main() -> int:
    if not GRAPH.exists():
        print("FAIL: graph/repository_graph.json missing. Run scripts/graph/build_repository_graph.py")
        return 1
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    node_ids = {n.get("id") for n in nodes}
    failures = []

    if not nodes:
        failures.append("graph has no nodes")

    required_types = {"policy", "adr", "wbs", "runbook", "workflow", "script"}
    present = {n.get("type") for n in nodes}
    missing_types = required_types - present
    if missing_types:
        failures.append(f"missing node types: {sorted(missing_types)}")

    for e in edges:
        if e.get("source") not in node_ids:
            failures.append(f"edge source missing: {e}")
        if e.get("target") not in node_ids:
            failures.append(f"edge target missing: {e}")

    if failures:
        print("# Repository Graph Validation")
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print("# Repository Graph Validation")
    print(f"PASS: nodes={len(nodes)} edges={len(edges)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
