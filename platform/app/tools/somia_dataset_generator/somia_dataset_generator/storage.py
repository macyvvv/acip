from pathlib import Path
import hashlib
import json
import os
import tempfile

def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def write_jsonl(path: Path, rows: list[dict]) -> None:
    atomic_write_text(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
