#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required = [
        ROOT / 'docs' / 'current' / 'LOW_RISK_ROOT_MIGRATION_PACK.md',
        ROOT / 'packs' / 'PACK-0008-low-risk-root-migration' / 'pack.yaml',
        ROOT / 'runtime' / 'root_hygiene' / 'low_risk_root_migration_plan.json',
        ROOT / 'tests' / 'test_low_risk_root_migration_plan.py',
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        print('FAIL: missing PACK-0008 files:', ', '.join(missing))
        return 1
    print('PACK-0008 validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
