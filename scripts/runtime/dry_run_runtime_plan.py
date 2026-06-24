#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "graph" / "agent_context_pack.json"
OUT = ROOT / "runtime" / "runtime_dry_run_report.md"

def main() -> int:
    if not PACK.exists():
        print("agent context pack missing. Run scripts/context/build_agent_context_pack.py")
        return 1
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    lines = [
        "# Runtime Dry Run Report",
        "",
        "## Conclusion",
        "",
        "Runtime dry-run completed without external actions.",
        "",
        "## Boundary",
        "",
        "- Runtime execution: not performed",
        "- External API calls: not performed",
        "- Repository mutation: report generation only",
        "- Secret use: not performed",
        "",
        "## Context",
        "",
        f"- node_count: {pack.get('node_count')}",
        f"- edge_count: {pack.get('edge_count')}",
        f"- current_phase: {pack.get('current_phase')}",
        f"- current_objective: {pack.get('current_objective')}",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"dry_run_report={OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
