from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CodexIntakeTriggerContract:
    trigger_id: str
    source: str
    pack_id: str
    ep_id: str
    approval_required: bool
    next_action: str
