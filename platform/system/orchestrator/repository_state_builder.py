from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json

from system.orchestrator.queue_state import read_queue_state


@dataclass(frozen=True)
class RepositoryStateProjection:
    active_pack: str
    active_ep: str
    latest_completion: dict
    queue_status: str
    validation_status: str
    pytest_status: str
    worktree_state: str
    approval_required: bool
    pending_review_items: list[str]
    repository_health: str
    runtime_health: str
    next_action: str
    source_artifacts: list[str]


class RepositoryStateBuilder:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def _path(self, *parts: str) -> Path:
        system_path = self.base_path / "system" / Path(*parts)
        legacy_path = self.base_path / Path(*parts)
        return system_path if system_path.exists() or not legacy_path.exists() else legacy_path

    def build(self) -> RepositoryStateProjection:
        queue_state = read_queue_state(self.base_path / "docs" / "current" / "QUEUE_STATE.md")
        latest_completion = self._read_json(self._path("runtime", "handoff", "latest.json"))
        latest_completion_fallback = self._read_json(self._path("runtime", "handoff", "completion", "latest.json"))
        completion = latest_completion or latest_completion_fallback or {}
        validation_state = self._read_validation_state()
        repo_constitution = self._read_json(self._path("runtime", "repository_constitution", "constitution.json"))
        packs = self._read_pack_ids()
        pending_review_items = self._pending_review_items(queue_state.status, completion)
        source_artifacts = [
            "platform/system/runtime/handoff/latest.json",
            "platform/system/runtime/handoff/completion/latest.json",
            "platform/system/runtime/event_runtime/",
            "queue/",
            "platform/system/runtime/validation/",
            "platform/system/runtime/repository_constitution/constitution.json",
            "platform/packs/",
        ]
        if (self.base_path / "docs" / "current" / "PACK_0005_EXECUTION_RECORD.md").exists():
            source_artifacts.append("platform/docs/current/PACK_0005_EXECUTION_RECORD.md")
        if (self.base_path / "docs" / "current" / "PACK_0003_EXECUTION_RECORD.md").exists():
            source_artifacts.append("platform/docs/current/PACK_0003_EXECUTION_RECORD.md")
        return RepositoryStateProjection(
            active_pack=completion.get("pack_id", packs[0] if packs else "unknown"),
            active_ep=completion.get("ep_id", queue_state.next_ep),
            latest_completion=completion,
            queue_status=queue_state.status,
            validation_status=validation_state.get("last_validation_status", "unknown"),
            pytest_status=validation_state.get("last_pytest_status", validation_state.get("last_validation_status", "unknown")),
            worktree_state=completion.get("worktree_state", "unknown"),
            approval_required=bool(completion.get("requires_human_approval", False)),
            pending_review_items=pending_review_items,
            repository_health=self._repository_health(validation_state, completion, repo_constitution),
            runtime_health=self._runtime_health(),
            next_action=completion.get("next_action", queue_state.next_ep),
            source_artifacts=source_artifacts,
        )

    def write(self, state: RepositoryStateProjection) -> None:
        payload = asdict(state)
        for runtime_dir in (self.base_path / "system" / "runtime" / "repository_state", self.base_path / "runtime" / "repository_state"):
            runtime_dir.mkdir(parents=True, exist_ok=True)
            (runtime_dir / "latest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (runtime_dir / "latest.md").write_text(self._to_markdown(state), encoding="utf-8")
            (runtime_dir / "repository_state.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (runtime_dir / "REPOSITORY_STATE.md").write_text(self._to_markdown(state), encoding="utf-8")

    def _to_markdown(self, state: RepositoryStateProjection) -> str:
        return "\n".join([
            "# REPOSITORY_STATE",
            "",
            f"active_pack: {state.active_pack}",
            f"active_ep: {state.active_ep}",
            f"queue_status: {state.queue_status}",
            f"validation_status: {state.validation_status}",
            f"pytest_status: {state.pytest_status}",
            f"worktree_state: {state.worktree_state}",
            f"approval_required: {str(state.approval_required).lower()}",
            f"repository_health: {state.repository_health}",
            f"runtime_health: {state.runtime_health}",
            f"next_action: {state.next_action}",
            "",
        ])

    def _read_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_validation_state(self) -> dict:
        path = self.base_path / "docs" / "current" / "VALIDATION_STATE.md"
        if not path.exists():
            return {}
        result: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result

    def _read_pack_ids(self) -> list[str]:
        registry = self.base_path / "packs" / "registry.yaml"
        if not registry.exists():
            return []
        ids: list[str] = []
        for line in registry.read_text(encoding="utf-8").splitlines():
            if line.startswith("- pack_id:"):
                ids.append(line.split(":", 1)[1].strip())
        return ids

    def _pending_review_items(self, queue_status: str, completion: dict) -> list[str]:
        items: list[str] = []
        if queue_status != "DONE":
            items.append(f"queue:{queue_status}")
        if completion.get("requires_human_approval"):
            items.append("human_approval_required")
        return items

    def _repository_health(self, validation_state: dict, completion: dict, repo_constitution: dict) -> str:
        if not repo_constitution:
            return "degraded"
        if validation_state.get("last_validation_status") != "success":
            return "degraded"
        if completion.get("status") not in {"success", "complete"}:
            return "degraded"
        return "healthy"

    def _runtime_health(self) -> str:
        if self._path("runtime", "event_runtime", "dry_run.json").exists():
            return "healthy"
        return "unknown"
