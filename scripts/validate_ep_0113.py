#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "workers" / "registry.py",
        ROOT / "workers" / "registry.yaml",
        ROOT / "docs" / "current" / "WORKER_REGISTRY.md",
        ROOT / "docs" / "ep" / "README_EP0113_WORKER_REGISTRY.md",
        ROOT / "specs" / "EP-0113",
        ROOT / ".github" / "workflows" / "ep0113-worker-registry.yml",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing worker registry files:", ", ".join(missing))
        return 1

    from workers.registry import load_worker_registry

    registry = load_worker_registry(ROOT / "workers" / "registry.yaml")
    for worker_name in ["Codex", "ChatGPT", "Human", "GitHub Actions"]:
        if not registry.has(worker_name):
            print(f"FAIL: missing worker entry: {worker_name}")
            return 1

    print("EP-0113 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
