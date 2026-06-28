from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class RuntimeArtifactWritePolicy:
    registry: tuple[str, ...]
    explicit_refresh_only: bool = True

    def can_write(self, path: str, *, explicit_refresh: bool = False) -> bool:
        if self.explicit_refresh_only and not explicit_refresh:
            return False
        return path in self.registry


class RuntimeArtifactPolicyLoader:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def load(self) -> RuntimeArtifactWritePolicy:
        registry_path = self.base_path / "runtime" / "generated_artifacts" / "generated_artifacts.json"
        if not registry_path.exists():
            return RuntimeArtifactWritePolicy(registry=())
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        return RuntimeArtifactWritePolicy(registry=tuple(payload.get("generated_artifacts", ())))

