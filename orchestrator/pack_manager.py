from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import yaml


@dataclass(frozen=True)
class Pack:
    pack_id: str
    name: str
    objective: str
    scope: str
    ep_range: tuple[str, str]
    dependencies: tuple[str, ...]
    done_conditions: tuple[str, ...]


class PackManagerError(ValueError):
    pass


class PackManager:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def load_registry(self) -> tuple[Pack, ...]:
        registry_path = self.base_path / "packs" / "registry.yaml"
        if not registry_path.exists():
            return ()
        raw = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or []
        packs = tuple(self._parse_pack(item) for item in raw)
        self.validate(packs)
        return packs

    def validate(self, packs: tuple[Pack, ...]) -> None:
        pack_ids = [pack.pack_id for pack in packs]
        if len(pack_ids) != len(set(pack_ids)):
            raise PackManagerError("Duplicate pack id detected")
        for pack in packs:
            if not self._valid_ep_range(pack.ep_range):
                raise PackManagerError(f"Invalid ep_range for {pack.pack_id}")

    def _parse_pack(self, item: dict) -> Pack:
        return Pack(
            pack_id=item["pack_id"],
            name=item["name"],
            objective=item["objective"],
            scope=item["scope"],
            ep_range=tuple(item["ep_range"]),
            dependencies=tuple(item.get("dependencies", [])),
            done_conditions=tuple(item.get("done_conditions", [])),
        )

    def _valid_ep_range(self, ep_range: tuple[str, str]) -> bool:
        if len(ep_range) != 2:
            return False
        return ep_range[0] <= ep_range[1]

