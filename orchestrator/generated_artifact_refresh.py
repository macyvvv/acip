from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from orchestrator.generated_artifact_manager import GeneratedArtifactManager
from orchestrator.validation_orchestrator import ValidationOrchestrator


@dataclass(frozen=True)
class GeneratedArtifactRefreshResult:
    validation_success: bool
    generated_artifact_count: int


class GeneratedArtifactRefresh:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def refresh(self) -> GeneratedArtifactRefreshResult:
        validation_orchestrator = ValidationOrchestrator(self.base_path)
        result = validation_orchestrator.run()
        validation_orchestrator.write_reports(result)

        manager = GeneratedArtifactManager(self.base_path)
        report = manager.report_dirty(self._git_status())
        manager.write_runtime_report(report)

        return GeneratedArtifactRefreshResult(
            validation_success=result.overall_success,
            generated_artifact_count=len(report.generated_artifacts),
        )

    def _git_status(self) -> list[str]:
        import subprocess

        completed = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.base_path,
            capture_output=True,
            text=True,
            check=False,
        )
        dirty_paths = []
        for line in completed.stdout.splitlines():
            if len(line) >= 4:
                dirty_paths.append(line[3:].strip())
        return dirty_paths

