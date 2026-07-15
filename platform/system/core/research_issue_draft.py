from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _runtime_path(base_path: Path | str | None, *parts: str) -> Path:
    root = Path(base_path) if base_path is not None else Path(".")
    return root / "system" / "runtime" / Path(*parts)


def load_issue_draft_registry(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    path = _runtime_path(base_path, "research", "issue_draft_registry.json")
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def build_issue_draft_registry(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    research_dir = _runtime_path(base_path, "research")
    registry: list[dict[str, Any]] = []
    draft_path = research_dir / "issue_draft_opp_kabukicho_001.json"
    if draft_path.exists():
        draft = json.loads(draft_path.read_text(encoding="utf-8"))
        registry.append(
            {
                "draft_id": "DRAFT-OPP-KABUKICHO-001",
                "source_opportunity_id": draft.get("opportunity_id", ""),
                "title": draft.get("title", ""),
                "status": "draft",
                "ready_for_issue_creation": False,
                "target_product_scope": "platform/app/products/kabukicho_survival_map_mvp",
                "dependencies": draft.get("dependencies", []),
                "validation_readiness": "ready",
                "created_from": "platform/system/runtime/research/issue_draft_opp_kabukicho_001.json",
            }
        )
    return registry


def write_issue_draft_registry(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    registry = build_issue_draft_registry(base_path)
    runtime_dir = _runtime_path(base_path, "research")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "issue_draft_registry.json").write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (runtime_dir / "issue_draft_registry.md").write_text(_to_markdown(registry), encoding="utf-8")
    return registry


def intake_issue_draft(base_path: Path | str | None = None, draft_id: str = "DRAFT-OPP-KABUKICHO-001") -> dict[str, Any]:
    registry = load_issue_draft_registry(base_path)
    entry = next((item for item in registry if item.get("draft_id") == draft_id), None)
    if entry is None:
        registry = write_issue_draft_registry(base_path)
        entry = next((item for item in registry if item.get("draft_id") == draft_id), None)
    if entry is None:
        raise ValueError(f"Unknown draft_id: {draft_id}")
    return {
        "draft_id": entry["draft_id"],
        "source_opportunity_id": entry["source_opportunity_id"],
        "title": entry["title"],
        "status": entry["status"],
        "ready_for_issue_creation": bool(entry["ready_for_issue_creation"]),
        "target_product_scope": entry["target_product_scope"],
        "dependencies": entry["dependencies"],
        "validation_readiness": entry["validation_readiness"],
        "created_from": entry["created_from"],
    }


def _to_markdown(registry: list[dict[str, Any]]) -> str:
    lines = ["# ISSUE_DRAFT_REGISTRY", ""]
    for entry in registry:
        lines.extend(
            [
                f"## {entry.get('draft_id', '')}",
                f"- source_opportunity_id: {entry.get('source_opportunity_id', '')}",
                f"- title: {entry.get('title', '')}",
                f"- status: {entry.get('status', '')}",
                f"- ready_for_issue_creation: {str(entry.get('ready_for_issue_creation', False)).lower()}",
                f"- target_product_scope: {entry.get('target_product_scope', '')}",
                f"- validation_readiness: {entry.get('validation_readiness', '')}",
                f"- created_from: {entry.get('created_from', '')}",
                "",
            ]
        )
    return "\n".join(lines)
