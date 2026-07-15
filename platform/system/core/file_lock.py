from __future__ import annotations

import fcntl
import time
from contextlib import contextmanager
from pathlib import Path

DEFAULT_LOCK_TIMEOUT_SECONDS = 5.0


class FileLockTimeout(TimeoutError):
    pass


@contextmanager
def locked(path: str | Path, *, timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS):
    """Advisory exclusive lock over a real file's read-modify-write cycle,
    via fcntl.flock (held by the OS against the file descriptor, released
    automatically on process death -- unlike an O_EXCL lockfile, which can
    deadlock permanently if the holder is killed). Only needed for state
    genuinely shared across concurrent invocations (business_agent_tasks/
    queue.json, knowledge/kpi.json) -- per-task-scoped files never need
    this, since no two processes legitimately touch the same task's file.

    Raises FileLockTimeout on timeout rather than retrying silently: this
    is human-driven CLI usage (occasional overlap), not a hot loop, so a
    clear failure is better than a stuck silent retry."""
    lock_path = Path(str(path) + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as lock_file:
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise FileLockTimeout(f"Timed out waiting for lock on {path} after {timeout_seconds}s")
                time.sleep(0.05)
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
