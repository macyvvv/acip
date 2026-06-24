from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class RuntimeContext:
    repository_root: str
    current_phase: str
    current_objective: str
    graph_path: str
    context_pack_path: str
    node_count: int
    edge_count: int
    boundary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimePlan:
    plan_id: str
    objective: str
    steps: list[str]
    validation: list[str]
    prohibited_actions: list[str]
    approval_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QueueItem:
    task_id: str
    owner: str
    objective: str
    status: str
    validation: str
    done_condition: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReviewSummary:
    summary_id: str
    decision: str
    evidence: list[str]
    risks: list[str]
    human_decision_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
