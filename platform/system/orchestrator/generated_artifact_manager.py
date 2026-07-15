from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class GeneratedArtifact:
    path: str
    generated_by: str


@dataclass(frozen=True)
class GeneratedArtifactReport:
    generated_artifacts: tuple[GeneratedArtifact, ...]
    generated_only_dirty: tuple[str, ...]
    manual_dirty: tuple[str, ...]


class GeneratedArtifactManager:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def load_manifest(self) -> tuple[GeneratedArtifact, ...]:
        manifest = self.base_path / "docs" / "current" / "GENERATED_ARTIFACTS.md"
        if not manifest.exists():
            return ()
        artifacts: list[GeneratedArtifact] = []
        for line in manifest.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("- `") and "`" in line[3:]:
                path = line.split("`", 2)[1]
                generated_by = "validate_all.py"
                artifacts.append(GeneratedArtifact(path=path, generated_by=generated_by))
        return tuple(artifacts)

    def report_dirty(self, dirty_paths: list[str]) -> GeneratedArtifactReport:
        artifacts = self.load_manifest()
        generated_paths = {artifact.path for artifact in artifacts}
        generated_only_dirty = tuple(sorted(path for path in dirty_paths if path in generated_paths))
        manual_dirty = tuple(sorted(path for path in dirty_paths if path not in generated_paths))
        return GeneratedArtifactReport(
            generated_artifacts=artifacts,
            generated_only_dirty=generated_only_dirty,
            manual_dirty=manual_dirty,
        )

    def write_runtime_report(self, report: GeneratedArtifactReport) -> None:
        runtime_dir = self.base_path / "runtime" / "generated_artifacts"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_artifacts": [
                {"path": artifact.path, "generated_by": artifact.generated_by}
                for artifact in report.generated_artifacts
            ],
            "generated_only_dirty": list(report.generated_only_dirty),
            "manual_dirty": list(report.manual_dirty),
        }
        (runtime_dir / "generated_artifacts.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        lines = ["# GENERATED_ARTIFACTS", ""]
        for artifact in report.generated_artifacts:
            lines.append(f"- `{artifact.path}`")
        (runtime_dir / "GENERATED_ARTIFACTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
