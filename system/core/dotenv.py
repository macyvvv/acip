from __future__ import annotations

from pathlib import Path
import os


def load_dotenv(path: str | Path = ".env") -> dict[str, str]:
    """Minimal .env loader: KEY=VALUE per line, '#' comments, blank lines
    skipped. If a key appears more than once in the file, the last
    occurrence wins (normal dotenv semantics). Never overrides a variable
    already present in the real environment before this call, so
    `FOO=bar python3 script.py` still wins over the file."""
    env_path = Path(path)
    loaded: dict[str, str] = {}
    if not env_path.exists():
        return loaded
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        loaded[key] = value  # last occurrence in the file wins
    for key, value in loaded.items():
        if key not in os.environ:
            os.environ[key] = value
    return loaded
