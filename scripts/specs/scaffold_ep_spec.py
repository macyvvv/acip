#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ep_id")
    args = parser.parse_args()
    spec_dir = ROOT / "specs" / args.ep_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    print(f"scaffolded={spec_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
