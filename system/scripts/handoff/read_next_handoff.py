#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

from orchestrator.codex_intake import CodexIntake


def main() -> int:
    intake = CodexIntake(ROOT)
    payload = intake.read_next_handoff()
    request = intake.to_execution_request(payload)
    runtime_dir = ROOT / "runtime" / "intake"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "handoff.json").write_text(
        "\n".join(
            [
                "{",
                f'  "request_id": "{request.request_id}",',
                f'  "pack_id": "{payload.pack_id}",',
                f'  "queue_path": "{payload.queue_path}"',
                "}",
            ]
        ),
        encoding="utf-8",
    )
    print(payload.queue_path)
    print(request.request_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
