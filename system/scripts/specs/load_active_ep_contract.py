#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
def load_active_ep_contract() -> dict[str, object]:
    path = ROOT / "specs" / "EP-0104" / "ep_contract.yaml"
    data: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("  - "):
            if current_key is None:
                continue
            data.setdefault(current_key, [])
            items = data[current_key]
            if isinstance(items, list):
                items.append(line[4:])
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            data[key] = value if value else []
    return data


def main() -> int:
    print(json.dumps(load_active_ep_contract(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
