#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
GRAPH = ROOT / "graph" / "repository_graph.json"
OUT = ROOT / "graph" / "agent_context_pack.json"

def main() -> int:
    if not GRAPH.exists():
        print("graph missing; building first")
        import subprocess, sys
        subprocess.check_call([sys.executable, "scripts/graph/build_repository_graph.py"], cwd=ROOT)

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    pack = {
        "pack_id": "ACP-0001",
        "actor_profiles": {
            "Human": ["Mission", "Approval", "Emergency Stop", "Risk Acceptance", "Capital Allocation", "Runtime Transition Approval"],
            "ChatGPT": ["CSO", "Review", "Priority", "Planning", "Delegation"],
            "Codex": ["Implementation", "Test", "Commit"],
        },
        "current_phase": "Knowledge Factory",
        "current_objective": "Repository Operating System Stabilization",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "required_boundaries": [
            "Repository overrides conversation",
            "Runtime implementation remains out of scope until explicitly approved",
            "Human handles Mission / Approval / Emergency Stop",
        ],
        "source_files": [n["path"] for n in nodes if n.get("type") in {"policy", "adr", "wbs", "runbook", "contract", "workflow"}],
        "validation_commands": [
            "python scripts/graph/build_repository_graph.py",
            "python scripts/graph/validate_repository_graph.py",
            "python scripts/context/build_agent_context_pack.py",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"context_pack={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
