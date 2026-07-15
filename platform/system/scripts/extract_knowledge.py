#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
INBOX = ROOT / "inbox" / "chat_logs"
KNOWLEDGE = ROOT / "knowledge"


@dataclass(frozen=True)
class ExtractedKnowledge:
    decisions: list[str]
    ideas: list[str]
    tasks: list[str]
    keywords: list[str]
    risks: list[str]
    adr_candidates: list[str]
    parking_lot: list[str]


def extract_knowledge_from_text(text: str) -> ExtractedKnowledge:
    decisions = _collect_prefixed(text, ["decision", "decisions"])
    ideas = _collect_prefixed(text, ["idea", "ideas"])
    tasks = _collect_prefixed(text, ["task", "tasks"])
    risks = _collect_prefixed(text, ["risk", "risks"])
    adr_candidates = _collect_prefixed(text, ["adr", "adr candidate", "adr candidates"])
    parking_lot = _collect_prefixed(text, ["parking lot", "defer", "deferred"])
    keywords = _keywords(text)
    return ExtractedKnowledge(decisions, ideas, tasks, keywords, risks, adr_candidates, parking_lot)


def extract_from_files(paths: Iterable[Path]) -> ExtractedKnowledge:
    aggregate = ExtractedKnowledge([], [], [], [], [], [], [])
    for path in sorted(paths):
        extracted = extract_knowledge_from_text(path.read_text(encoding="utf-8"))
        aggregate = ExtractedKnowledge(
            decisions=_merge(aggregate.decisions, extracted.decisions),
            ideas=_merge(aggregate.ideas, extracted.ideas),
            tasks=_merge(aggregate.tasks, extracted.tasks),
            keywords=_merge(aggregate.keywords, extracted.keywords),
            risks=_merge(aggregate.risks, extracted.risks),
            adr_candidates=_merge(aggregate.adr_candidates, extracted.adr_candidates),
            parking_lot=_merge(aggregate.parking_lot, extracted.parking_lot),
        )
    return aggregate


def update_knowledge_files(extracted: ExtractedKnowledge, base_path: Path | str | None = None) -> dict[str, Path]:
    root = Path(base_path) if base_path is not None else ROOT
    knowledge_dir = root / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "dashboard": knowledge_dir / "dashboard.md",
        "current_state": knowledge_dir / "current_state.md",
        "ideas": knowledge_dir / "ideas.md",
        "decision_log": knowledge_dir / "decision_log.md",
        "glossary": knowledge_dir / "glossary.md",
        "knowledge_graph": knowledge_dir / "knowledge_graph.md",
        "parking_lot": knowledge_dir / "parking_lot.md",
    }
    _write_section(outputs["decision_log"], "# KNOWLEDGE_DECISION_LOG", "Decisions", extracted.decisions)
    _write_section(outputs["ideas"], "# KNOWLEDGE_IDEAS", "Ideas", extracted.ideas)
    _write_section(outputs["current_state"], "# KNOWLEDGE_CURRENT_STATE", "Current State", extracted.tasks)
    _write_section(outputs["glossary"], "# KNOWLEDGE_GLOSSARY", "Keywords", extracted.keywords)
    _write_section(outputs["knowledge_graph"], "# KNOWLEDGE_GRAPH", "ADR Candidates", extracted.adr_candidates)
    _write_section(outputs["parking_lot"], "# KNOWLEDGE_PARKING_LOT", "Parking Lot", extracted.parking_lot)
    outputs["dashboard"].write_text(
        "\n".join([
            "# KNOWLEDGE_DASHBOARD",
            "",
            f"- decisions: {len(extracted.decisions)}",
            f"- ideas: {len(extracted.ideas)}",
            f"- tasks: {len(extracted.tasks)}",
            f"- keywords: {len(extracted.keywords)}",
            f"- risks: {len(extracted.risks)}",
            f"- adr_candidates: {len(extracted.adr_candidates)}",
            f"- parking_lot: {len(extracted.parking_lot)}",
            "",
        ]),
        encoding="utf-8",
    )
    return outputs


def main() -> int:
    INBOX.mkdir(parents=True, exist_ok=True)
    logs = sorted([path for path in INBOX.iterdir() if path.is_file() and path.suffix.lower() in {".md", ".txt"}])
    extracted = extract_from_files(logs)
    outputs = update_knowledge_files(extracted, ROOT)
    print(json.dumps({
        "processed_logs": [str(path.relative_to(ROOT)) for path in logs],
        "decisions": len(extracted.decisions),
        "ideas": len(extracted.ideas),
        "tasks": len(extracted.tasks),
        "keywords": len(extracted.keywords),
        "risks": len(extracted.risks),
        "adr_candidates": len(extracted.adr_candidates),
        "parking_lot": len(extracted.parking_lot),
        "outputs": {key: str(path.relative_to(ROOT)) for key, path in outputs.items()},
    }, indent=2, ensure_ascii=False))
    return 0


def _collect_prefixed(text: str, prefixes: list[str]) -> list[str]:
    results: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        for prefix in prefixes:
            marker = f"{prefix}:"
            if lower.startswith(marker):
                results.append(stripped[len(marker):].strip())
                break
    return _unique(results)


def _keywords(text: str) -> list[str]:
    matches = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", text)
    filtered = [word.lower() for word in matches if word.lower() not in {"http", "https", "the", "and", "with", "that"}]
    return _unique(sorted(filtered))


def _merge(existing: list[str], incoming: list[str]) -> list[str]:
    return _unique(existing + incoming)


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _write_section(path: Path, title: str, heading: str, items: list[str]) -> None:
    lines = [title, "", f"## {heading}"]
    lines.extend(f"- {item}" for item in items)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
