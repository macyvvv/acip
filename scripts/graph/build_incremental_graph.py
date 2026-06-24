#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "graph" / "repository_graph.json"
OUT = ROOT / "graph" / "repository_graph_delta.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    if not GRAPH.exists():
        subprocess.check_call([sys.executable, "scripts/graph/build_repository_graph.py"], cwd=ROOT)

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = graph.get("nodes", [])
    snapshot = []
    for n in nodes:
        p = ROOT / n["path"]
        if p.exists() and p.is_file():
            snapshot.append({
                "id": n["id"],
                "path": n["path"],
                "type": n.get("type"),
                "sha256": sha(p),
            })

    delta = {
        "baseline": "1.0.0-repository-os",
        "node_count": len(nodes),
        "snapshot_count": len(snapshot),
        "snapshot": snapshot,
    }
    OUT.write_text(json.dumps(delta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"incremental_graph={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
