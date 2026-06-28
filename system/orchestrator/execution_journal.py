from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime, timezone


@dataclass(frozen=True)
class ExecutionJournalEntry:
    timestamp: str
    session_id: str
    worker_name: str
    request_id: str
    result: str
    review: str


class ExecutionJournal:
    def __init__(self, base_path: str | Path = ".") -> None:
        self.base_path = Path(base_path)

    def append(self, entry: ExecutionJournalEntry) -> None:
        runtime_dir = self.base_path / "runtime" / "journal"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        json_path = runtime_dir / "execution_journal.jsonl"
        with json_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry.__dict__, ensure_ascii=False) + "\n")
        md_path = runtime_dir / "EXECUTION_JOURNAL.md"
        existing = md_path.read_text(encoding="utf-8") if md_path.exists() else "# EXECUTION_JOURNAL\n\n"
        md_path.write_text(
            existing
            + f"- {entry.timestamp} | session={entry.session_id} | worker={entry.worker_name} | request={entry.request_id} | result={entry.result}\n",
            encoding="utf-8",
        )

    def new_entry(
        self,
        session_id: str,
        worker_name: str,
        request_id: str,
        result: str,
        review: str,
    ) -> ExecutionJournalEntry:
        return ExecutionJournalEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=session_id,
            worker_name=worker_name,
            request_id=request_id,
            result=result,
            review=review,
        )
