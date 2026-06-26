#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def main() -> int:
    required_paths = [
        ROOT / "graph" / "repository_graph.json",
        ROOT / "graph" / "repository_graph.md",
        ROOT / "graph" / "agent_context_pack.json",
        ROOT / "orchestrator" / "context_bundle.json",
        ROOT / "orchestrator" / "execution_plan.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0100 artifacts:", ", ".join(missing))
        return 1
    import subprocess
    cmd = [sys.executable, "scripts/agent_runtime/validate_agent_runtime_mvp.py"]
    print("$ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)
    print("EP-0100 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
