from __future__ import annotations

from pathlib import Path

from orchestrator.event_runtime_dry_run import EventRuntimeDryRun


def run_cli(fixture_path: str | Path, base_path: str | Path = ".") -> str:
    result = EventRuntimeDryRun(base_path).run_issue_fixture(fixture_path)
    return result.dry_run_path
