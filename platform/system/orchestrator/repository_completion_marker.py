from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

from system.orchestrator.completion_protocol import CompletionProtocol


@dataclass(frozen=True)
class RepositoryCompletionMarker:
    completion: CompletionProtocol
    latest_path: str
    history_path: str


class RepositoryCompletionMarkerWriter:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def write(self, completion: CompletionProtocol) -> RepositoryCompletionMarker:
        runtime_dir = self.base_path / "runtime" / "handoff"
        history_dir = runtime_dir / "completion" / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(completion)
        payload["status"] = completion.status.value
        latest_path = runtime_dir / "latest.json"
        history_path = history_dir / f"{completion.pack_id}.json"
        latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        (runtime_dir / "completion" / "latest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        history_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return RepositoryCompletionMarker(completion=completion, latest_path=str(latest_path), history_path=str(history_path))
