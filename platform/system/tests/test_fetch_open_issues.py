from __future__ import annotations

import json
import subprocess
from pathlib import Path

from system.scripts.github.fetch_open_issues import fetch_open_issues, write_open_issue_mirror


def test_fetch_open_issues_writes_json_and_md(tmp_path: Path, monkeypatch) -> None:
    def fake_run(command, capture_output, text, check):
        assert command == ["gh", "issue", "list", "--state", "open", "--json", "number,title,state"]
        return type(
            "Result",
            (),
            {"returncode": 0, "stdout": json.dumps([{"number": 34, "title": "PRODUCT-0003: Kabukicho Map Data Expansion", "state": "OPEN"}]), "stderr": ""},
        )()

    monkeypatch.setattr("system.scripts.github.fetch_open_issues.subprocess.run", fake_run)
    monkeypatch.setattr("system.scripts.github.fetch_open_issues._repo_root", lambda: tmp_path)

    issues = fetch_open_issues()
    output_path = write_open_issue_mirror(issues, tmp_path)

    assert issues == [{"number": 34, "title": "PRODUCT-0003: Kabukicho Map Data Expansion", "state": "open"}]
    assert output_path == tmp_path / "system" / "runtime" / "github" / "open_issues.json"
    assert json.loads(output_path.read_text(encoding="utf-8")) == issues
    assert "PRODUCT-0003: Kabukicho Map Data Expansion" in (tmp_path / "system" / "runtime" / "github" / "open_issues.md").read_text(encoding="utf-8")


def test_fetch_open_issues_handles_empty_list(tmp_path: Path, monkeypatch) -> None:
    def fake_run(command, capture_output, text, check):
        return type("Result", (), {"returncode": 0, "stdout": "[]", "stderr": ""})()

    monkeypatch.setattr("system.scripts.github.fetch_open_issues.subprocess.run", fake_run)
    monkeypatch.setattr("system.scripts.github.fetch_open_issues._repo_root", lambda: tmp_path)

    issues = fetch_open_issues()
    output_path = write_open_issue_mirror(issues, tmp_path)

    assert issues == []
    assert json.loads(output_path.read_text(encoding="utf-8")) == []
    assert (tmp_path / "system" / "runtime" / "github" / "open_issues.md").read_text(encoding="utf-8").strip() == "# Open Issues Mirror"


def test_fetch_open_issues_rewrites_stale_entries(tmp_path: Path, monkeypatch) -> None:
    def fake_run(command, capture_output, text, check):
        return type(
            "Result",
            (),
            {"returncode": 0, "stdout": json.dumps([{"number": 35, "title": "PRODUCT-0004: Fresh Issue", "state": "open"}]), "stderr": ""},
        )()

    monkeypatch.setattr("system.scripts.github.fetch_open_issues.subprocess.run", fake_run)
    monkeypatch.setattr("system.scripts.github.fetch_open_issues._repo_root", lambda: tmp_path)

    stale_path = tmp_path / "system" / "runtime" / "github" / "open_issues.json"
    stale_path.parent.mkdir(parents=True, exist_ok=True)
    stale_path.write_text(json.dumps([{"number": 99, "title": "STALE", "state": "open"}]), encoding="utf-8")

    issues = fetch_open_issues()
    write_open_issue_mirror(issues, tmp_path)

    assert json.loads(stale_path.read_text(encoding="utf-8")) == [{"number": 35, "title": "PRODUCT-0004: Fresh Issue", "state": "open"}]
