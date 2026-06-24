from __future__ import annotations

from pathlib import Path
import json

from .models import RuntimeContext
from .repository import assert_required_files


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_runtime_context(root: Path) -> RuntimeContext:
    assert_required_files(root)

    graph_path = root / "graph" / "repository_graph.json"
    context_pack_path = root / "graph" / "agent_context_pack.json"

    graph = load_json(graph_path)
    pack = load_json(context_pack_path)

    return RuntimeContext(
        repository_root=str(root),
        current_phase=pack.get("current_phase", "Runtime Preparation"),
        current_objective=pack.get("current_objective", "Agent Runtime Foundation"),
        graph_path="graph/repository_graph.json",
        context_pack_path="graph/agent_context_pack.json",
        node_count=len(graph.get("nodes", [])),
        edge_count=len(graph.get("edges", [])),
        boundary={
            "runtime_execution": "not_performed",
            "external_actions": "prohibited",
            "secret_use": "prohibited",
            "human_boundary": "Mission / Approval / Emergency Stop",
            "repository_rule": "Repository overrides conversation",
        },
    )
