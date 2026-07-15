from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TargetLayoutContract:
    root_allowlist: tuple[str, ...]
    migration_policy: str
