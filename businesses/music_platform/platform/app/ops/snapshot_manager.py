#!/usr/bin/env python3
"""A-006a/A-007 snapshot and fallback wiring for DB artifact."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

from ops_common import make_run_id, write_json


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Manage immutable DB snapshots")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("snapshot", help="Create immutable snapshot")
    s1.add_argument("--db", required=True, help="Source DB path")
    s1.add_argument(
        "--snapshots-dir",
        default="businesses/music_platform/runtime/ops/snapshots",
        help="Snapshot directory",
    )
    s1.add_argument(
        "--manifest",
        default="businesses/music_platform/runtime/ops/snapshots/rollback_manifest_latest.json",
        help="Manifest output",
    )

    s2 = sub.add_parser("restore", help="Restore DB from snapshot")
    s2.add_argument("--snapshot", required=True, help="Snapshot DB path")
    s2.add_argument("--db", required=True, help="Target DB path")

    s3 = sub.add_parser("fallback", help="Restore latest good snapshot")
    s3.add_argument(
        "--manifest",
        default="businesses/music_platform/runtime/ops/snapshots/rollback_manifest_latest.json",
        help="Manifest path",
    )
    s3.add_argument("--db", required=True, help="Target DB path")

    return p.parse_args()


def cmd_snapshot(args: argparse.Namespace) -> int:
    src = Path(args.db)
    run_id = make_run_id("snapshot")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshots_dir = Path(args.snapshots_dir)
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    dst = snapshots_dir / f"bandoff_research_merged_{ts}.db"
    shutil.copy2(src, dst)

    checksum = sha256_file(dst)
    manifest = {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_db": str(src),
        "snapshot_db": str(dst),
        "sha256": checksum,
    }
    write_json(Path(args.manifest), manifest)
    print(str(dst))
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    src = Path(args.snapshot)
    dst = Path(args.db)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print("restored")
    return 0


def cmd_fallback(args: argparse.Namespace) -> int:
    manifest = Path(args.manifest)
    data = manifest.read_text(encoding="utf-8")
    import json

    m = json.loads(data)
    src = Path(m["snapshot_db"])
    dst = Path(args.db)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print("fallback_done")
    return 0


def main() -> int:
    args = parse_args()
    if args.cmd == "snapshot":
        return cmd_snapshot(args)
    if args.cmd == "restore":
        return cmd_restore(args)
    if args.cmd == "fallback":
        return cmd_fallback(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
