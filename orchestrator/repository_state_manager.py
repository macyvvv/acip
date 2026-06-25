from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from orchestrator.generated_artifact_manager import GeneratedArtifactManager
from orchestrator.queue_state import read_queue_state


@dataclass(frozen=True)
class RepositoryState:
    queue_status: str
    active_ep: str
    next_ep: str
    validation_status: str
    generated_artifacts_dirty: tuple[str, ...] = ()
    manual_dirty: tuple[str, ...] = ()


class RepositoryStateManager:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def build_state(self, dirty_paths: list[str] | None = None) -> RepositoryState:
        queue_state = read_queue_state(self.base_path / "docs" / "current" / "QUEUE_STATE.md")
        validation_status = self._read_validation_status()
        artifact_manager = GeneratedArtifactManager(self.base_path)
        report = artifact_manager.report_dirty(dirty_paths or [])
        return RepositoryState(
            queue_status=queue_state.status,
            active_ep=queue_state.active_ep,
            next_ep=queue_state.next_ep,
            validation_status=validation_status,
            generated_artifacts_dirty=report.generated_only_dirty,
            manual_dirty=report.manual_dirty,
        )

    def write_runtime_state(self, state: RepositoryState) -> None:
        runtime_dir = self.base_path / "runtime" / "repository_state"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "queue_status": state.queue_status,
            "active_ep": state.active_ep,
            "next_ep": state.next_ep,
            "validation_status": state.validation_status,
            "generated_artifacts_dirty": list(state.generated_artifacts_dirty),
            "manual_dirty": list(state.manual_dirty),
        }
        (runtime_dir / "repository_state.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (runtime_dir / "REPOSITORY_STATE.md").write_text(
            "\n".join(
                [
                    "# REPOSITORY_STATE",
                    "",
                    f"queue_status: {state.queue_status}",
                    f"active_ep: {state.active_ep}",
                    f"next_ep: {state.next_ep}",
                    f"validation_status: {state.validation_status}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _read_validation_status(self) -> str:
        path = self.base_path / "docs" / "current" / "VALIDATION_STATE.md"
        if not path.exists():
            return "unknown"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("last_validation_status:"):
                return line.split(":", 1)[1].strip()
        return "unknown"
