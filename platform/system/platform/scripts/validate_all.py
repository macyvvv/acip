from __future__ import annotations

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[2] / "scripts" / "validate_all.py"), run_name="__main__")