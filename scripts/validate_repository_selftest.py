#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "selftest"))
from validate_repository_selftest_complete import main
raise SystemExit(main())
