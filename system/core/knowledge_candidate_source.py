from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _knowledge_root(base_path: Path | str | None = None) -> Path:
    root = Path(base_path) if base_path is not None else Path(".")
    return root / "knowledge"


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def load_knowledge_assets(base_path: Path | str | None = None) -> dict[str, list[str]]:
    root = _knowledge_root(base_path)
    assets = {
        "decisions": _extract_bullets(root / "decision_log.md") or _extract_bullets(root / "decisions.md"),
        "ideas": _extract_bullets(root / "ideas.md"),
        "tasks": _extract_bullets(root / "current_state.md") or _extract_bullets(root / "tasks.md"),
        "risks": _extract_bullets(root / "parking_lot.md") or _extract_bullets(root / "risks.md"),
        "adrs": _extract_bullets(root / "knowledge_graph.md") or _extract_bullets(root / "adrs.md"),
        "parking_lot": _extract_bullets(root / "parking_lot.md"),
    }
    return assets


def build_knowledge_candidates(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    assets = load_knowledge_assets(base_path)
    candidates: list[dict[str, Any]] = []
    for source_asset, entry_type, usable_by in [
        ("decisions.md", "context", "both"),
        ("ideas.md", "opportunity_seed", "research"),
        ("tasks.md", "work_item", "planner"),
        ("risks.md", "risk_signal", "both"),
        ("adrs.md", "architecture_constraint", "planner"),
        ("parking_lot.md", "deferred_candidate", "both"),
    ]:
        key = source_asset.split(".")[0]
        for index, text in enumerate(assets.get(key, []), start=1):
            candidate_id = f"KC-{key.upper()}-{index:04d}"
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "source_asset": source_asset,
                    "entry_type": entry_type,
                    "title": text.split(":")[0].strip()[:120],
                    "normalized_text": text.strip(),
                    "source": "knowledge_asset_registry",
                    "proposed_pack_or_ep": "KNOWLEDGE-INPUT",
                    "objective": text.strip(),
                    "rationale": text.strip(),
                    "draft_id": None,
                    "source_opportunity_id": None,
                    "ready_for_issue_creation": False,
                    "mission_contribution": 1,
                    "management_cost_reduction": 1,
                    "risk_reduction": 1,
                    "strategic_value": 1,
                    "operational_value": 1,
                    "learning_value": 1,
                    "dependencies": [],
                    "blocked_by": [],
                    "approval_required": False,
                    "recommended_next_action": _recommended_action(entry_type),
                    "recommended_action": _recommended_action(entry_type),
                    "issue_body_draft": text.strip(),
                    "usable_by": usable_by,
                }
            )
    return _dedupe_candidates(candidates)


def persist_knowledge_candidates(base_path: Path | str | None = None) -> list[dict[str, Any]]:
    candidates = build_knowledge_candidates(base_path)
    root = Path(base_path) if base_path is not None else Path(".")
    runtime_dir = root / "system" / "runtime" / "knowledge"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "knowledge_candidates.json").write_text(json.dumps(candidates, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (runtime_dir / "knowledge_candidates.md").write_text(_to_markdown(candidates), encoding="utf-8")
    return candidates


def _extract_bullets(path: Path) -> list[str]:
    lines = _read_lines(path)
    bullets = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def _dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    ordered: list[dict[str, Any]] = []
    for candidate in candidates:
        key = (candidate["source_asset"], candidate["normalized_text"])
        if key in seen:
            continue
        seen.add(key)
        ordered.append(candidate)
    return ordered


def _recommended_action(entry_type: str) -> str:
    mapping = {
        "context": "use_as_context",
        "opportunity_seed": "review_for_research",
        "work_item": "consider_for_planning",
        "risk_signal": "review_risk",
        "architecture_constraint": "apply_constraint",
        "deferred_candidate": "keep_in_parking_lot",
    }
    return mapping.get(entry_type, "review")


def _to_markdown(candidates: list[dict[str, Any]]) -> str:
    lines = ["# KNOWLEDGE_CANDIDATES", ""]
    for candidate in candidates:
        lines.extend(
            [
                f"## {candidate['candidate_id']}",
                f"- source_asset: {candidate['source_asset']}",
                f"- entry_type: {candidate['entry_type']}",
                f"- title: {candidate['title']}",
                f"- normalized_text: {candidate['normalized_text']}",
                f"- recommended_next_action: {candidate['recommended_next_action']}",
                f"- usable_by: {candidate['usable_by']}",
                "",
            ]
        )
    return "\n".join(lines)
