from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class State:
    repository: str
    branch: str
    current_milestone: str
    current_phase: str
    current_objective: str
    current_epic: str
    current_task: str
    next_action: str


class StateParseError(ValueError):
    pass


def read_state(path: str | Path = "docs/current/CURRENT_STATE.md") -> State:
    state_path = Path(path)
    if not state_path.exists():
        raise FileNotFoundError(f"State file not found: {state_path}")

    text = state_path.read_text(encoding="utf-8")
    fields = _parse_fields(text)

    required = [
        "repository",
        "branch",
        "current_milestone",
        "current_phase",
        "current_objective",
        "current_epic",
        "current_task",
        "next_action",
    ]
    missing = [field for field in required if not fields.get(field)]
    if missing:
        raise StateParseError(f"Missing required state fields: {', '.join(missing)}")

    return State(
        repository=fields["repository"],
        branch=fields["branch"],
        current_milestone=fields["current_milestone"],
        current_phase=fields["current_phase"],
        current_objective=fields["current_objective"],
        current_epic=fields["current_epic"],
        current_task=fields["current_task"],
        next_action=fields["next_action"],
    )


def _parse_fields(text: str) -> dict[str, str]:
    sections = _split_sections(text)
    repository_owner, repository_name = _parse_repository_section(sections.get("Repository", ""))
    repository = f"{repository_owner}/{repository_name}" if repository_owner and repository_name else ""

    return {
        "repository": repository,
        "branch": _first_content_line(sections.get("Repository", ""), label="Branch"),
        "current_milestone": _first_content_line(sections.get("Current Milestone", "")),
        "current_phase": _first_content_line(sections.get("Current Phase", "")),
        "current_objective": _section_body(sections.get("Current Objective", "")),
        "current_epic": _first_content_line(sections.get("Current Epic", "")),
        "current_task": _section_body(sections.get("Current Task", "")),
        "next_action": _section_body(sections.get("Current Next Action", "")),
    }


def _split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# "):
            current_heading = line[2:].strip()
            sections.setdefault(current_heading, [])
            continue
        if line.strip() == "---":
            continue
        if current_heading is not None:
            sections[current_heading].append(line)

    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def _parse_repository_section(section: str) -> tuple[str, str]:
    owner = _first_label_value(section, "GitHub Account")
    name = _first_label_value(section, "Repository")
    return owner, name


def _first_label_value(section: str, label: str) -> str:
    lines = section.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == label:
            for value_line in lines[index + 1 :]:
                value = value_line.strip()
                if value and not value.startswith("#"):
                    return value
    return ""


def _first_content_line(section: str, label: str | None = None) -> str:
    lines = section.splitlines()
    if label is not None:
        return _first_label_value(section, label)
    for line in lines:
        value = line.strip()
        if value and not value.startswith("Status"):
            return value
    return ""


def _section_body(section: str) -> str:
    return "\n".join(
        line.strip()
        for line in section.splitlines()
        if line.strip() and line.strip() != "Status" and line.strip() != "Doing"
    )
