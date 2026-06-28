from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from system.orchestrator.runtime_artifact_policy import RuntimeArtifactPolicyLoader


@dataclass(frozen=True)
class WorktreeCleanlinessResult:
    clean: bool
    dirty_paths: tuple[str, ...]
    manual_dirty_paths: tuple[str, ...]
    generated_dirty_paths: tuple[str, ...]


class WorktreeCleanlinessGate:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def evaluate(self) -> WorktreeCleanlinessResult:
        dirty_paths = self._git_status()
        registry = RuntimeArtifactPolicyLoader(self.base_path).load()
        generated_dirty_paths = tuple(sorted(path for path in dirty_paths if path in registry.registry))
        manual_dirty_paths = tuple(sorted(path for path in dirty_paths if path not in registry.registry))
        return WorktreeCleanlinessResult(
            clean=not dirty_paths,
            dirty_paths=tuple(sorted(dirty_paths)),
            manual_dirty_paths=manual_dirty_paths,
            generated_dirty_paths=generated_dirty_paths,
        )

    def _git_status(self) -> tuple[str, ...]:
        completed = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.base_path,
            capture_output=True,
            text=True,
            check=False,
        )
        paths = []
        for line in completed.stdout.splitlines():
            if len(line) >= 4:
                paths.append(line[3:].strip())
        return tuple(paths)

