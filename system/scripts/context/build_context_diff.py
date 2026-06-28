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
PACK = ROOT / "graph" / "agent_context_pack.json"
DELTA = ROOT / "graph" / "repository_graph_delta.json"
OUT = ROOT / "graph" / "context_diff.json"

def main() -> int:
    if not PACK.exists():
        subprocess.check_call([sys.executable, "system/scripts/context/build_agent_context_pack.py"], cwd=ROOT)
    if not DELTA.exists():
        subprocess.check_call([sys.executable, "system/scripts/graph/build_incremental_graph.py"], cwd=ROOT)

    pack = json.loads(PACK.read_text(encoding="utf-8"))
    delta = json.loads(DELTA.read_text(encoding="utf-8"))
    diff = {
        "baseline": "1.0.0-repository-os",
        "current_phase": pack.get("current_phase"),
        "current_objective": pack.get("current_objective"),
        "node_count": pack.get("node_count"),
        "edge_count": pack.get("edge_count"),
        "snapshot_count": delta.get("snapshot_count"),
        "status": "derived",
        "runtime_execution": "not_performed",
    }
    OUT.write_text(json.dumps(diff, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"context_diff={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
