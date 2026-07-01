from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _runtime_path(base_path: Path | str | None, *parts: str) -> Path:
    root = Path(base_path) if base_path is not None else Path(".")
    return root / "system" / "runtime" / Path(*parts)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, type(default)) else default


def build_issue_creation_drafts(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    approved_path = _runtime_path(base_path, "research", "approved_issue_drafts.json")
    approved_drafts = _load_json(approved_path, [])
    issue_creation_drafts: list[dict[str, Any]] = []
    for index, draft in enumerate(sorted(approved_drafts, key=lambda item: item.get("draft_id", "")), start=1):
        if not isinstance(draft, dict):
            continue
        if not bool(draft.get("approved_from_review_gate", False)):
            continue
        issue_creation_drafts.append(
            {
                "creation_draft_id": f"ICD-{index:04d}",
                "draft_id": draft.get("draft_id", ""),
                "source_opportunity_id": draft.get("source_opportunity_id", ""),
                "title": draft.get("title", ""),
                "issue_body_draft": draft.get("issue_body_draft", ""),
                "target_product_scope": draft.get("target_product_scope", ""),
                "dependencies": list(draft.get("dependencies", [])),
                "validation_readiness": draft.get("validation_readiness", ""),
                "source": draft.get("source", "research_issue_draft_registry"),
                "review_status": "approved",
                "ready_for_manual_github_issue_creation": True,
            }
        )
    return issue_creation_drafts


def persist_issue_creation_drafts(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    drafts = build_issue_creation_drafts(base_path)
    runtime_dir = _runtime_path(base_path, "research")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "issue_creation_drafts.json").write_text(json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (runtime_dir / "issue_creation_drafts.md").write_text(_to_markdown(drafts), encoding="utf-8")
    return drafts


def _to_markdown(drafts: list[dict[str, Any]]) -> str:
    lines = ["# ISSUE_CREATION_DRAFTS", ""]
    for draft in drafts:
        lines.extend(
            [
                f"## {draft.get('creation_draft_id', '')}",
                f"- draft_id: {draft.get('draft_id', '')}",
                f"- source_opportunity_id: {draft.get('source_opportunity_id', '')}",
                f"- title: {draft.get('title', '')}",
                f"- target_product_scope: {draft.get('target_product_scope', '')}",
                f"- review_status: {draft.get('review_status', '')}",
                f"- ready_for_manual_github_issue_creation: {str(draft.get('ready_for_manual_github_issue_creation', False)).lower()}",
                "",
            ]
        )
    return "\n".join(lines)
