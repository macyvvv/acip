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
sys.path.insert(0,str(ROOT))
def main()->int:
 required=[ROOT/"queue"/"READY"/"EP-0188-work-discovery-loop.md",ROOT/"orchestrator"/"local_supervisor.py",ROOT/"docs"/"current"/"WORK_DISCOVERY_LOOP.md",ROOT/"specs"/"EP-0188",ROOT/"tests"/"test_local_supervisor.py"]
 missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
 if missing:
  print("FAIL: missing EP-0188 files:", ", ".join(missing)); return 1
 print("EP-0188 Validation passed."); return 0
if __name__=="__main__": raise SystemExit(main())
