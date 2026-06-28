from __future__ import annotations

from system.orchestrator.execution_journal import ExecutionJournal


def test_execution_journal_builds_entry() -> None:
    journal = ExecutionJournal(".")
    entry = journal.new_entry("SESSION-1", "Codex", "REQ-1", "success", "ok")
    assert entry.worker_name == "Codex"
