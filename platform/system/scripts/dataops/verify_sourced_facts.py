from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

# DataOps verification step (added 2026-07-15) after an audit found
# doc_creation fabricating specific facts about named products no
# market_research artifact had ever covered -- a materially wrong Perplexity
# Pro price and invented "70%/50%" savings percentages, both hand-caught by
# a human before publication with nothing in the pipeline itself preventing
# it. Heuristic, not exhaustive: flags any specific numeric figure (price,
# percentage, unit) in a draft that doesn't appear in ANY market_research
# artifact for the same business, as a candidate for human review -- a
# coincidental match isn't proof of real sourcing, and this can't verify
# WHICH product a number was about, only whether the number itself has any
# textual precedent in this business's research. A real, concrete, checkable
# signal is better than a prose promise, but it is not a substitute for a
# human actually reading the draft.

_FIGURE_PATTERN = re.compile(
    r"(?:[$¥€£]\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?(?:%|円|ドル|分/月|分|GB|MB|件))"
)


def extract_figures(text: str) -> set[str]:
    return {match.strip() for match in _FIGURE_PATTERN.findall(text)}


def _normalize(figure: str) -> str:
    return re.sub(r"[\s,]", "", figure)


def _stdout_of(business_id: str, role_id: str, task_id: str, base_path: str | Path) -> str:
    path = Path(base_path) / "system/runtime/business_agents" / business_id / role_id / task_id / "latest.json"
    if not path.exists():
        raise FileNotFoundError(f"No artifact at {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str(payload.get("stdout") or "")


def sourced_figures_for_business(business_id: str, base_path: str | Path = ".") -> set[str]:
    research_root = Path(base_path) / "system/runtime/business_agents" / business_id / "market_research"
    figures: set[str] = set()
    if not research_root.exists():
        return figures
    for artifact_path in research_root.glob("*/latest.json"):
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        figures |= extract_figures(str(payload.get("stdout") or ""))
    return figures


def verify_sourced_facts(business_id: str, role_id: str, task_id: str, base_path: str | Path = ".") -> list[str]:
    """Returns the sorted list of figures in the draft with no textual match
    anywhere in this business's market_research artifacts. Empty means every
    figure in the draft has at least one precedent in research -- a
    necessary, not sufficient, condition for real sourcing."""
    draft_text = _stdout_of(business_id, role_id, task_id, base_path)
    draft_figures = extract_figures(draft_text)
    if not draft_figures:
        return []
    sourced = {_normalize(f) for f in sourced_figures_for_business(business_id, base_path)}
    return sorted(f for f in draft_figures if _normalize(f) not in sourced)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that every specific figure (price/percentage/limit) in a doc_creation or "
        "marketing draft has at least one textual match in this business's market_research artifacts. "
        "Heuristic candidate-flagging for human review, not an automatic content judge."
    )
    parser.add_argument("business_id")
    parser.add_argument("role_id")
    parser.add_argument("task_id")
    args = parser.parse_args()

    unsourced = verify_sourced_facts(args.business_id, args.role_id, args.task_id, ROOT)
    if unsourced:
        print(f"unsourced_figures={len(unsourced)}")
        for figure in unsourced:
            print(f"  - {figure}")
        print("These figures have no textual match in any market_research artifact for this business.")
        print("Review manually: either cut/generalize them, or confirm the matching research exists elsewhere.")
        return 1

    print("unsourced_figures=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
