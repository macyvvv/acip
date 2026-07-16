#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "platform"))
runpy.run_path(str(ROOT / "platform" / "system" / "scripts" / "validate_ep_0108.py"), run_name="__main__")
