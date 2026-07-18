#!/usr/bin/env python3
"""Convenience wrapper so `python run_bandoff_once.py` works from repo root.

Delegates to the crawler package runner under
businesses/music_platform/platform/app/crawler.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CRAWLER_DIR = ROOT / "businesses" / "music_platform" / "platform" / "app" / "crawler"

if str(CRAWLER_DIR) not in sys.path:
    sys.path.insert(0, str(CRAWLER_DIR))

runpy.run_path(str(CRAWLER_DIR / "run_bandoff_once.py"), run_name="__main__")
