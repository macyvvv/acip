from __future__ import annotations

from system.orchestrator.state import State
from system.orchestrator.task import Task, TaskValidationError


def state_to_task(state: State) -> Task:
    fields = _parse_next_action(state.next_action)
    artifact = fields.get("artifact", "")
    owner = fields.get("owner", "")
    done_conditions = fields.get("definition of done", "")

    missing = []
    if not artifact:
        missing.append("Artifact")
    if not owner:
        missing.append("Owner")
    if not done_conditions:
        missing.append("Done Conditions")
    if missing:
        raise TaskValidationError(f"Missing required task fields: {', '.join(missing)}")

    return Task(
        id=f"{state.current_epic}:{artifact}",
        artifact=artifact,
        owner=owner,
        instruction=state.next_action.strip(),
        done_conditions=done_conditions,
        target_paths=(),
    )


def _parse_next_action(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    current_label: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_label, current_lines
        if current_label is not None:
            values[current_label] = "\n".join(current_lines).strip()
        current_label = None
        current_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line in {"Artifact", "Owner", "Definition of Done"}:
            flush()
            current_label = line.lower()
            continue
        if current_label is not None:
            current_lines.append(line)

    flush()
    return values
