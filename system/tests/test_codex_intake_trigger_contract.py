from __future__ import annotations

from system.orchestrator.codex_intake_trigger_contract import CodexIntakeTriggerContract


def test_codex_intake_trigger_contract_dataclass() -> None:
    contract = CodexIntakeTriggerContract("trigger-1", "issue", "PACK-0006", "EP-0170", False, "run")
    assert contract.pack_id == "PACK-0006"
