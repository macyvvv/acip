from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ResearchContext:
    planning: dict[str, Any]
    repository_state: dict[str, Any]
    existing_opportunities: list[dict[str, Any]]
    existing_insights: list[dict[str, Any]]


def _runtime_path(base_path: Path | str | None, *parts: str) -> Path:
    root = Path(base_path) if base_path is not None else Path(".")
    return root / "system" / "runtime" / Path(*parts)


def load_research_request(base_path: Path | str | None = None) -> dict[str, Any]:
    path = _runtime_path(base_path, "research", "request_example.json")
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_research_context(base_path: Path | str | None = None) -> ResearchContext:
    planning = _read_json(_runtime_path(base_path, "planning", "latest.json"))
    repository_state = _read_json(_runtime_path(base_path, "repository_state", "latest.json"))
    existing_opportunities = _read_json(_runtime_path(base_path, "research", "opportunities.json"))
    existing_insights = _read_json(_runtime_path(base_path, "research", "insights.json"))
    return ResearchContext(
        planning=planning,
        repository_state=repository_state,
        existing_opportunities=existing_opportunities if isinstance(existing_opportunities, list) else [],
        existing_insights=existing_insights if isinstance(existing_insights, list) else [],
    )


def generate_research_output(request: dict[str, Any], context: ResearchContext) -> dict[str, Any]:
    topic = str(request.get("topic", "")).strip()
    normalized_topic = topic.lower()
    facts = _facts_for_topic(normalized_topic, context)
    assumptions = _assumptions_for_topic(normalized_topic, context)
    hypotheses = _hypotheses_for_topic(normalized_topic, context)
    recommendations = _recommendations_for_topic(normalized_topic, context)
    opportunities = _opportunities_for_topic(request, normalized_topic, facts, hypotheses, recommendations)
    return {
        "request_id": str(request.get("request_id", "")),
        "topic": topic,
        "facts": facts,
        "assumptions": assumptions,
        "hypotheses": hypotheses,
        "recommendations": recommendations,
        "opportunities": opportunities,
    }


def write_research_artifacts(base_path: Path | str | None, output: dict[str, Any]) -> dict[str, Path]:
    runtime_dir = _runtime_path(base_path, "research")
    runtime_dir.mkdir(parents=True, exist_ok=True)
    latest_json = runtime_dir / "latest.json"
    latest_md = runtime_dir / "latest.md"
    opportunities_json = runtime_dir / "opportunities.json"
    insights_json = runtime_dir / "insights.json"
    latest_json.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    latest_md.write_text(_to_markdown(output), encoding="utf-8")
    opportunities_json.write_text(json.dumps(output.get("opportunities", []), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    insights_json.write_text(json.dumps(output.get("hypotheses", []), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "latest_json": latest_json,
        "latest_md": latest_md,
        "opportunities_json": opportunities_json,
        "insights_json": insights_json,
    }


def _facts_for_topic(topic: str, context: ResearchContext) -> list[str]:
    facts = ["Repository-native research artifacts are deterministic."]
    if "kabukicho" in topic:
        facts.extend([
            "Kabukicho is a location-specific product scope.",
            "Map usefulness depends on user intent, local context, and actionable navigation data.",
        ])
    if context.repository_state.get("repository_health"):
        facts.append(f"Repository health: {context.repository_state.get('repository_health')}.")
    return facts


def _assumptions_for_topic(topic: str, context: ResearchContext) -> list[str]:
    assumptions = ["Research questions will be handed off before implementation."]
    if "kabukicho" in topic:
        assumptions.append("Users likely need local decision support rather than a generic map.")
    if context.planning.get("current_objective"):
        assumptions.append(f"Current objective context: {context.planning.get('current_objective')}.")
    return assumptions


def _hypotheses_for_topic(topic: str, context: ResearchContext) -> list[str]:
    hypotheses = ["Higher intent, lower-friction content will outperform generic listings."]
    if "kabukicho" in topic:
        hypotheses.extend([
            "Visitors and workers need concise route and safety cues.",
            "SEO opportunities likely cluster around intent-based local search queries.",
        ])
    if context.existing_insights:
        hypotheses.append("Existing insight history can be used to de-duplicate repeated claims.")
    return hypotheses


def _recommendations_for_topic(topic: str, context: ResearchContext) -> list[str]:
    recommendations = ["Prioritize validated user pain points over feature expansion."]
    if "kabukicho" in topic:
        recommendations.extend([
            "Interview local visitors and repeat workers.",
            "Test search intent clusters before expanding map data.",
            "Compare nearby alternatives to isolate differentiation.",
        ])
    if context.existing_opportunities:
        recommendations.append("Reuse existing opportunities rather than inventing parallel tracks.")
    return recommendations


def _opportunities_for_topic(
    request: dict[str, Any],
    topic: str,
    facts: list[str],
    hypotheses: list[str],
    recommendations: list[str],
) -> list[dict[str, Any]]:
    if "kabukicho" not in topic:
        return []
    target_user = str(request.get("target_user", "Kabukicho users"))
    evidence = [facts[1] if len(facts) > 1 else facts[0], hypotheses[0]]
    return [
        {
            "opportunity_id": "OPP-KABUKICHO-001",
            "title": "Kabukicho Survival Map MVP expansion research",
            "problem": "Users need faster decisions about local navigation and safety-relevant context.",
            "target_user": target_user,
            "expected_value": "Higher utility and better content targeting for local search intent.",
            "evidence": evidence,
            "confidence": "medium",
            "recommended_next_action": "Draft a research-backed issue for search intent and user segment validation.",
        }
    ]


def _to_markdown(output: dict[str, Any]) -> str:
    lines = [
        "# MARKETING_RESEARCH_AGENT_RESULT",
        "",
        f"request_id: {output.get('request_id', '')}",
        f"topic: {output.get('topic', '')}",
        "",
        "## Facts",
    ]
    lines.extend(f"- {item}" for item in output.get("facts", []))
    lines.extend(["", "## Assumptions"])
    lines.extend(f"- {item}" for item in output.get("assumptions", []))
    lines.extend(["", "## Hypotheses"])
    lines.extend(f"- {item}" for item in output.get("hypotheses", []))
    lines.extend(["", "## Recommendations"])
    lines.extend(f"- {item}" for item in output.get("recommendations", []))
    lines.extend(["", "## Opportunities"])
    for item in output.get("opportunities", []):
        lines.append(f"- {item.get('opportunity_id', '')}: {item.get('title', '')}")
    lines.append("")
    return "\n".join(lines)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
