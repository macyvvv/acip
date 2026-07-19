from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True, slots=True)
class PlanItem:
    slot: int
    character_id: str
    dimensions: dict[str, str]
    prompt: str
    specification_version: int
    policy_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
