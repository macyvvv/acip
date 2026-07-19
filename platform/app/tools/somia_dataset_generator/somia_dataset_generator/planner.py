from itertools import cycle
from .models import PlanItem
from .prompt_builder import build_prompt

def _expanded(values: dict[str, int]) -> list[str]:
    result: list[str] = []
    for name, count in values.items():
        if count < 0:
            raise ValueError("sampling weight/count must be non-negative")
        result.extend([name] * count)
    if not result:
        raise ValueError("sampling dimension cannot be empty")
    return result

def create_plan(character: dict, policy: dict, count: int) -> list[PlanItem]:
    if count <= 0:
        raise ValueError("count must be positive")
    dims = policy["dimensions"]
    names = list(dims)
    streams = {name: cycle(_expanded(dims[name])) for name in names}
    items: list[PlanItem] = []
    for slot in range(1, count + 1):
        selected = {name: next(streams[name]) for name in names}
        items.append(PlanItem(
            slot=slot,
            character_id=character["character_id"],
            dimensions=selected,
            prompt=build_prompt(character, selected),
            specification_version=character["schema_version"],
            policy_id=policy["policy_id"],
        ))
    return items
