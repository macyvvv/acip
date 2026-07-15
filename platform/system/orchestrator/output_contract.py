from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationResult:
    command: str
    exit_code: int
    output: str = ""


@dataclass(frozen=True)
class WorktreeState:
    clean: bool
    changed_files: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CodexOutputContract:
    task_id: str
    validation_results: list[ValidationResult] = field(default_factory=list)
    commit_sha: str | None = None
    worktree_state: WorktreeState = field(default_factory=lambda: WorktreeState(clean=True))
    next_action: str = ""
    rerun_validation_conditions: list[str] = field(default_factory=list)


def build_output_contract(
    task_id: str,
    validation_results: list[ValidationResult],
    commit_sha: str | None,
    worktree_state: WorktreeState,
    next_action: str,
    rerun_validation_conditions: list[str],
) -> CodexOutputContract:
    return CodexOutputContract(
        task_id=task_id,
        validation_results=list(validation_results),
        commit_sha=commit_sha,
        worktree_state=worktree_state,
        next_action=next_action,
        rerun_validation_conditions=list(rerun_validation_conditions),
    )
