from __future__ import annotations

from pathlib import Path
import re


BROKEN_PREFIXES = ("system/system/", "agent_system/runtime/", "event_system/runtime/")
ROOT_AGENT_RUNTIME_PATTERN = re.compile(r"(?<!system/)agent_runtime/")


def _iter_executable_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if path.name == "test_legacy_path_references.py":
            continue
        if ".git" in path.parts or ".venv" in path.parts or ".pytest_cache" in path.parts:
            continue
        if path.suffix.lower() not in {".py", ".sh", ".yml", ".yaml"}:
            continue
        if "docs" in path.parts or "basis" in path.parts or "knowledge" in path.parts or "archive" in path.parts or "specs" in path.parts:
            continue
        files.append(path)
    return files


def test_no_legacy_root_paths_in_executable_code() -> None:
    root = Path(__file__).resolve().parents[2]
    offenders: list[str] = []
    for path in _iter_executable_files(root):
        text = path.read_text(encoding="utf-8")
        if any(prefix in text for prefix in BROKEN_PREFIXES):
            offenders.append(str(path.relative_to(root)))
            continue
        if ROOT_AGENT_RUNTIME_PATTERN.search(text) and "system/scripts/agent_runtime/" not in text and "system/agent_runtime/" not in text:
            offenders.append(str(path.relative_to(root)))
    assert offenders == []
