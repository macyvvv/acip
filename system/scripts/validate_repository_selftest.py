#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
V2 = ROOT / "scripts" / "selftest_v2"
if str(V2) not in sys.path:
    sys.path.insert(0, str(V2))

from validate_semantic_selftest import main

if __name__ == "__main__":
    raise SystemExit(main())
