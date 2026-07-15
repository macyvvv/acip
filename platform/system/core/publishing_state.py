from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system.core.file_lock import locked

# Sharded per (business_id, platform), NOT one shared file across every
# business -- ADR-0034 already rejected a single shared JSON file for
# per-task state for exactly this reason (unrelated businesses would
# contend on one flock, and one corrupted file would take down every
# business's/platform's publishing at once). Dedup + day/week counters
# live together in one file per shard so a check-then-increment sequence
# is atomic within one critical section.


class PublishingStateError(RuntimeError):
    pass


def _state_path(business_id: str, platform: str, base_path: str | Path = ".") -> Path:
    return Path(base_path) / "platform/system/runtime/publishing/state" / business_id / platform / "state.json"


def _default_state() -> dict[str, Any]:
    return {"published": {}, "counters": {}}


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        # Fail closed, not open: a corrupted state file must never be read as
        # "empty" -- that would silently forget dedup history and cap counts,
        # which is the direction (re-publish, blow through caps) a safety
        # mechanism must never fail in.
        raise PublishingStateError(f"{path} is corrupted and could not be parsed: {exc}") from exc
    if not isinstance(data, dict) or "published" not in data or "counters" not in data:
        raise PublishingStateError(f"{path} has an unexpected shape; refusing to treat it as empty")
    return data


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _dedup_key(role_id: str, task_id: str) -> str:
    return f"{role_id}:{task_id}"


def is_already_published(business_id: str, platform: str, role_id: str, task_id: str, base_path: str | Path = ".") -> bool:
    state = _load_state(_state_path(business_id, platform, base_path))
    return _dedup_key(role_id, task_id) in state["published"]


def counts_for_today(business_id: str, platform: str, base_path: str | Path = ".") -> int:
    state = _load_state(_state_path(business_id, platform, base_path))
    return int(state["counters"].get(_today_key(), 0))


def counts_for_week(business_id: str, platform: str, base_path: str | Path = ".") -> int:
    state = _load_state(_state_path(business_id, platform, base_path))
    return int(state["counters"].get(_week_key(), 0))


def record_publish(
    business_id: str,
    role_id: str,
    task_id: str,
    platform: str,
    provider: str,
    external_post_id: str | None,
    base_path: str | Path = ".",
) -> dict[str, Any]:
    path = _state_path(business_id, platform, base_path)
    with locked(path):
        state = _load_state(path)  # fresh read INSIDE the critical section, not a pre-lock snapshot
        dedup_key = _dedup_key(role_id, task_id)
        if dedup_key in state["published"]:
            raise PublishingStateError(
                f"{business_id}/{platform}/{dedup_key} was already published at "
                f"{state['published'][dedup_key].get('published_at')} -- refusing to double-publish"
            )
        entry = {
            "role_id": role_id,
            "task_id": task_id,
            "provider": provider,
            "external_post_id": external_post_id,
            "published_at": datetime.now(timezone.utc).isoformat(),
        }
        state["published"][dedup_key] = entry
        day_key, week_key = _today_key(), _week_key()
        state["counters"][day_key] = int(state["counters"].get(day_key, 0)) + 1
        state["counters"][week_key] = int(state["counters"].get(week_key, 0)) + 1
        _write_state(path, state)
        return entry


def _today_key() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _week_key() -> str:
    iso = datetime.now(timezone.utc).isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"
