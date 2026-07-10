from __future__ import annotations

import fcntl
from pathlib import Path

import pytest

from system.core.file_lock import FileLockTimeout, locked


def test_locked_allows_serial_use(tmp_path: Path) -> None:
    target = tmp_path / "shared.json"
    with locked(target):
        target.write_text("first", encoding="utf-8")
    with locked(target):
        target.write_text("second", encoding="utf-8")
    assert target.read_text(encoding="utf-8") == "second"


def test_locked_times_out_when_already_held(tmp_path: Path) -> None:
    target = tmp_path / "shared.json"
    lock_path = Path(str(target) + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    holder = open(lock_path, "w")
    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        with pytest.raises(FileLockTimeout):
            with locked(target, timeout_seconds=0.2):
                pass
    finally:
        fcntl.flock(holder, fcntl.LOCK_UN)
        holder.close()


def test_locked_releases_after_block(tmp_path: Path) -> None:
    target = tmp_path / "shared.json"
    with locked(target):
        pass
    # lock must be released -- a second acquisition should not time out
    with locked(target, timeout_seconds=0.2):
        pass
