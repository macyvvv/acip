from __future__ import annotations

import json
import subprocess
from pathlib import Path

from system.scripts.github.fetch_open_issues import fetch_open_issues, write_open_issue_mirror
from system.scripts.sync_github_issues import sync_github_issues


def test_issue_sync_writes_open_issues(tmp_path: Path, monkeypatch) -> None:
    def fake_run(command, capture_output, text, check):
        assert command == ["gh", "issue", "list", "--state", "open", "--json", "number,title,state"]
        return type("Result", (), {"returncode": 0, "stdout": json.dumps([{"number": 34, "title": "PRODUCT-0003: Kabukicho Map Data Expansion", "state": "open"}]), "stderr": ""})()

    monkeypatch.setattr("system.scripts.github.fetch_open_issues.subprocess.run", fake_run)
    monkeypatch.setattr("system.scripts.github.fetch_open_issues._repo_root", lambda: tmp_path)

    issues = fetch_open_issues()
    write_open_issue_mirror(issues, tmp_path)

    path = tmp_path / "system" / "runtime" / "github" / "open_issues.json"
    assert issues == [{"number": 34, "title": "PRODUCT-0003: Kabukicho Map Data Expansion", "state": "open"}]
    assert json.loads(path.read_text(encoding="utf-8")) == issues


def test_issue_sync_normalizes_state(tmp_path: Path, monkeypatch) -> None:
    def fake_run(command, capture_output, text, check):
        assert command == ["gh", "issue", "list", "--state", "open", "--json", "number,title,state"]
        return type("Result", (), {"returncode": 0, "stdout": json.dumps([{"number": 34, "title": "PRODUCT-0003: Kabukicho Map Data Expansion", "state": "OPEN"}]), "stderr": ""})()

    monkeypatch.setattr("system.scripts.github.fetch_open_issues.subprocess.run", fake_run)
    monkeypatch.setattr("system.scripts.github.fetch_open_issues._repo_root", lambda: tmp_path)

    issues = fetch_open_issues()
    write_open_issue_mirror(issues, tmp_path)

    path = tmp_path / "system" / "runtime" / "github" / "open_issues.json"
    assert issues == [{"number": 34, "title": "PRODUCT-0003: Kabukicho Map Data Expansion", "state": "open"}]
    assert json.loads(path.read_text(encoding="utf-8")) == issues


def test_issue_sync_does_not_write_on_failure(tmp_path: Path, monkeypatch) -> None:
    def fake_run(command, capture_output, text, check):
        raise subprocess.CalledProcessError(returncode=1, cmd=command, stderr="gh failed")

    monkeypatch.setattr("system.scripts.github.fetch_open_issues.subprocess.run", fake_run)
    monkeypatch.setattr("system.scripts.github.fetch_open_issues._repo_root", lambda: tmp_path)

    try:
        fetch_open_issues()
    except subprocess.CalledProcessError as exc:
        assert "gh failed" in str(exc.stderr)
    else:
        raise AssertionError("CalledProcessError not raised")

    assert not (tmp_path / "system" / "runtime" / "github" / "open_issues.json").exists()
