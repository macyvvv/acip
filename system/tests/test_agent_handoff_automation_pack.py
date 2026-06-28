from __future__ import annotations

from pathlib import Path


def test_agent_handoff_queue_item_exists() -> None:
    path = Path("queue/READY/EP-0144-agent-handoff-automation-pack.md")
    text = path.read_text(encoding="utf-8")
    assert "Remove Human from ChatGPT-to-Codex handoff" in text
    assert "queue/READY/" in text
