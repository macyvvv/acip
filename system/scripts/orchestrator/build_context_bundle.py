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
PACK = ROOT / "graph" / "agent_context_pack.json"
OUT = ROOT / "orchestrator" / "context_bundle.json"

def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    graph = load_json(GRAPH)
    pack = load_json(PACK)

    policy_nodes = [n for n in graph.get("nodes", []) if n.get("type") == "policy"]
    adr_nodes = [n for n in graph.get("nodes", []) if n.get("type") == "adr"]
    wbs_nodes = [n for n in graph.get("nodes", []) if n.get("type") == "wbs"]

    bundle = {
        "bundle_id": "OCB-0001",
        "current_phase": pack.get("current_phase", "Knowledge Factory"),
        "current_objective": "Canonical Agent Orchestration Preparation",
        "task_id": "ORCH-0001",
        "actor": "ChatGPT/Codex/scripts",
        "source_files": [n["path"] for n in policy_nodes + adr_nodes + wbs_nodes],
        "graph_nodes": len(graph.get("nodes", [])),
        "graph_edges": len(graph.get("edges", [])),
        "required_policies": [n["path"] for n in policy_nodes if "orchestrator" in n["path"] or "context" in n["path"]],
        "validation_commands": [
            "python system/scripts/system/orchestrator/build_context_bundle.py",
            "python system/scripts/system/orchestrator/build_execution_plan.py",
            "python system/scripts/system/orchestrator/validate_orchestration.py",
        ],
        "prohibited_actions": [
            "runtime agent execution",
            "auto posting",
            "platform API mutation",
            "scraping-dependent automation",
            "secret use",
            "approval bypass",
        ],
        "human_boundary": "Human handles Mission / Approval / Emergency Stop / Risk Acceptance / Capital Allocation / Runtime Transition Approval",
        "runtime_boundary": "Runtime execution remains prohibited until explicit Human approval",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"context_bundle={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
