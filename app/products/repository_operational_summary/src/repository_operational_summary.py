from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class RepositorySummary:
    mission: str | None
    current_objective: str | None
    repository_health: str | None
    validation_status: str | None
    worktree_state: str | None
    approval_required: bool | None


def load_summary(base_path: str | Path) -> RepositorySummary:
    root = Path(base_path)
    planning = _read_json(root / "runtime" / "planning" / "latest.json")
    repository = _read_json(root / "runtime" / "repository_state" / "latest.json")
    return RepositorySummary(
        mission=planning.get("mission"),
        current_objective=planning.get("current_objective"),
        repository_health=repository.get("repository_health"),
        validation_status=repository.get("validation_status"),
        worktree_state=repository.get("worktree_state"),
        approval_required=repository.get("approval_required"),
    )


def render_summary(summary: RepositorySummary) -> str:
    lines = ["Repository Operational Summary"]
    if summary.mission:
        lines.append(f"Mission: {summary.mission}")
    if summary.current_objective:
        lines.append(f"Current objective: {summary.current_objective}")
    if summary.repository_health:
        lines.append(f"Repository health: {summary.repository_health}")
    if summary.validation_status:
        lines.append(f"Validation status: {summary.validation_status}")
    if summary.worktree_state:
        lines.append(f"Worktree state: {summary.worktree_state}")
    if summary.approval_required is not None:
        lines.append(f"Approval required: {str(summary.approval_required).lower()}")
    return "\n".join(lines) + "\n"


def main(base_path: str | Path = ".") -> str:
    return render_summary(load_summary(base_path))


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
