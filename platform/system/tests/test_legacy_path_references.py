from __future__ import annotations

from pathlib import Path
import re


BROKEN_PREFIXES = (
    "platform/system/platform/system/",
    "agent_platform/system/runtime/",
    "event_platform/system/runtime/",
    # A duplicate "platform/system/platform/scripts/" legacy shim directory
    # (validate_all.py + root_hygiene/*.sh re-exec wrappers, byte-identical
    # to the real scripts at platform/system/scripts/) existed for a while
    # and drifted into ~40 files' worth of stale references before being
    # deleted 2026-07-17. Guarding here so it can't silently reappear.
    "platform/system/platform/scripts/",
)
ROOT_AGENT_RUNTIME_PATTERN = re.compile(r"(?<!platform/system/)agent_runtime/")


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
        if ROOT_AGENT_RUNTIME_PATTERN.search(text) and "platform/system/scripts/agent_runtime/" not in text and "platform/system/agent_runtime/" not in text:
            offenders.append(str(path.relative_to(root)))
    assert offenders == []
