from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "kabukicho_map_places.json"


def load_map_places() -> list[dict[str, str]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def render_places_section(places: list[dict[str, str]]) -> list[str]:
    grouped_places: dict[str, list[dict[str, str]]] = defaultdict(list)
    for place in places:
        grouped_places[str(place.get("category", "unknown"))].append(place)

    category_counts = Counter(str(place.get("category", "unknown")) for place in places)
    lines = [
        "## Expanded Map Data",
        "",
        "### Primary action",
        "Use the category filters first, then open the top POI detail block for quick confirmation.",
        "",
        "### Mobile guidance",
        "- One-hand use: start with the first visible filter or the top result.",
        "- Keep scanning short: confirm the summary, then decide whether to move.",
        "- Reduce noise: details are split into confirmed, caution, and gray-zone sections.",
        "",
        "### Category summary",
        *[f"- {category}: {count} place(s)" for category, count in sorted(category_counts.items())],
        "",
    ]
    for category in sorted(grouped_places):
        lines.extend(
            [
                f"### Category: {category}",
                "",
            ]
        )
        for place in grouped_places[category]:
            lines.append(
                "\n".join(
                    [
                        f"#### {place['name']}",
                        f"- Category: {place.get('category', 'unknown')}",
                        f"- Availability: {place.get('availability_type', 'unknown')}",
                        f"- Hours note: {place.get('hours_note', 'n/a')}",
                        f"- Cost note: {place.get('cost_note', 'n/a')}",
                        "",
                        "##### Confirmed information",
                        f"- {place.get('description', '')}",
                        f"- Source note: {place.get('source_note', 'n/a')}",
                        f"- Last verified: {place.get('last_verified_note', 'n/a')}",
                        "",
                        "##### Caution / uncertainty",
                        f"- {place.get('caution_note', 'n/a')}",
                        "",
                        "##### Gray-zone notes",
                        f"- {place.get('gray_zone_note', 'n/a')}",
                        "",
                    ]
                )
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
            "## Safety and Disclaimer",
            "- Confirm details before relying on any uncertain or unofficial information.",
            "- Gray-zone notes are advisory, not authoritative.",
            "- Community or venue-provided updates should be treated as reviewable input.",
            "",
            "## MVP Scope",
            "- Searchable place list",
            "- Simple map view",
            "- Incrementally expanded POI dataset",
            "- User-contributed notes",
            "- Moderation-friendly content model",
            "- Category-first mobile readability",
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
