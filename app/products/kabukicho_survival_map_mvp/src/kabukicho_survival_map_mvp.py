from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "kabukicho_map_places.json"


def load_map_places() -> list[dict[str, str]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def render_places_section(places: list[dict[str, str]]) -> list[str]:
    lines = ["## Expanded Map Data", ""]
    for place in places:
        lines.append(
            f"- {place['name']} ({place['category']}): {place['description']}"
        )
    lines.append("")
    return lines


def build_product_brief() -> str:
    places = load_map_places()
    return "\n".join(
        [
            "# Kabukicho Survival Map MVP",
            "",
            "## Purpose",
            "Define a small, reviewable product brief for a UGC-ready survival map with expanded place data.",
            "",
            "## Audience",
            "People who need a fast, practical map for Kabukicho risk-aware navigation and local discovery.",
            "",
            "## Value Proposition",
            "A concise map MVP that helps users identify useful places, avoid friction, and contribute verified updates.",
            "",
            "## MVP Scope",
            "- Searchable place list",
            "- Simple map view",
            "- User-contributed notes",
            "- Moderation-friendly content model",
            "",
            *render_places_section(places),
            "## Non-Goals",
            "- Live platform integrations",
            "- Automated posting",
            "- Unbounded user-generated content",
            "- Runtime agent behavior",
            "",
            "## Release Checklist",
            "- Scope is explicit",
            "- Audience is explicit",
            "- Value proposition is explicit",
            "- UGC boundaries are defined",
            "- Map data is expanded deterministically",
            "- Ready for repository review",
            "",
        ]
    )
