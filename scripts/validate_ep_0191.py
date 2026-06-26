#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
def main()->int:
 required=[ROOT/"queue"/"READY"/"EP-0191-completion-capture-adapter.md",ROOT/"orchestrator"/"local_supervisor.py",ROOT/"docs"/"current"/"COMPLETION_CAPTURE_ADAPTER.md",ROOT/"specs"/"EP-0191",ROOT/"tests"/"test_local_supervisor.py"]
 missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
 if missing:
  print("FAIL: missing EP-0191 files:", ", ".join(missing)); return 1
 print("EP-0191 Validation passed."); return 0
if __name__=="__main__": raise SystemExit(main())
