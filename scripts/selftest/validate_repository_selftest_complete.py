from __future__ import annotations

import importlib
import sys
from pathlib import Path

SELFTEST_DIR = Path(__file__).resolve().parent
if str(SELFTEST_DIR) not in sys.path:
    sys.path.insert(0, str(SELFTEST_DIR))

from selftest_common import print_results, CheckResult

CHECK_MODULES = [
    "check_repository_health",
    "check_boundaries",
    "check_secret_boundary",
    "check_link_integrity",
    "check_duplicates",
    "check_orphans",
    "check_workflows",
    "check_current_objective",
]

def main() -> int:
    all_results: list[CheckResult] = []
    for module_name in CHECK_MODULES:
        module = importlib.import_module(module_name)
        all_results.extend(module.run())
    return print_results("Repository Operating System Self Test Complete", all_results)

if __name__ == "__main__":
    raise SystemExit(main())
