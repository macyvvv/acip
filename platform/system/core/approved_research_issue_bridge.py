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


def _load_registry(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    return _load_json(_runtime_path(base_path, "research", "issue_draft_registry.json"), [])


def _load_review_decisions(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    return _load_json(_runtime_path(base_path, "research", "review_decisions.json"), [])


def build_approved_issue_drafts(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    registry = _load_registry(base_path)
    decisions = _load_review_decisions(base_path)
    approved_ids = [entry.get("draft_id", "") for entry in decisions if entry.get("decision_status") == "approved"]
    approved_entries: list[dict[str, Any]] = []
    for draft_id in sorted({draft_id for draft_id in approved_ids if draft_id}):
        registry_entry = next((entry for entry in registry if entry.get("draft_id") == draft_id), None)
        if registry_entry is None:
            continue
        draft_path = _runtime_path(base_path, "research", "issue_draft_opp_kabukicho_001.json")
        draft_payload = json.loads(draft_path.read_text(encoding="utf-8")) if draft_path.exists() else {}
        if not isinstance(draft_payload, dict):
            draft_payload = {}
        approved_entries.append(
            {
                "draft_id": registry_entry.get("draft_id", draft_id),
                "source_opportunity_id": registry_entry.get("source_opportunity_id", ""),
                "title": registry_entry.get("title", draft_payload.get("title", "")),
                "issue_body_draft": _issue_body_draft(draft_payload),
                "target_product_scope": registry_entry.get("target_product_scope", ""),
                "dependencies": list(registry_entry.get("dependencies", [])),
                "validation_readiness": registry_entry.get("validation_readiness", ""),
                "source": "research_issue_draft_registry",
                "approved_from_review_gate": True,
            }
        )
    return approved_entries


def persist_approved_issue_drafts(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    drafts = build_approved_issue_drafts(base_path)
    runtime_dir = _runtime_path(base_path, "research")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "approved_issue_drafts.json").write_text(json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (runtime_dir / "approved_issue_drafts.md").write_text(_to_markdown(drafts), encoding="utf-8")
    return drafts


def _issue_body_draft(draft: dict[str, Any]) -> str:
    lines = [
        f"# {draft.get('title', '')}",
        "",
        f"Objective: {draft.get('objective', '')}",
        "",
        "## Facts",
    ]
    lines.extend(f"- {item}" for item in draft.get("facts", []))
    lines.extend(
        [
            "",
            "## Assumptions",
        ]
    )
    lines.extend(f"- {item}" for item in draft.get("assumptions", []))
    lines.extend(
        [
            "",
            "## Recommendations",
        ]
    )
    lines.extend(f"- {item}" for item in draft.get("implementation_constraints", []))
    lines.append("")
    return "\n".join(lines)


def _to_markdown(drafts: list[dict[str, Any]]) -> str:
    lines = ["# APPROVED_RESEARCH_ISSUE_DRAFTS", ""]
    for draft in drafts:
        lines.extend(
            [
                f"## {draft.get('draft_id', '')}",
                f"- source_opportunity_id: {draft.get('source_opportunity_id', '')}",
                f"- title: {draft.get('title', '')}",
                f"- target_product_scope: {draft.get('target_product_scope', '')}",
                f"- validation_readiness: {draft.get('validation_readiness', '')}",
                f"- approved_from_review_gate: {str(draft.get('approved_from_review_gate', False)).lower()}",
                "",
            ]
        )
    return "\n".join(lines)
