#!/usr/bin/env python3
"""SQLite source-of-truth for Kabukicho POI data.

This script manages a DB-first workflow:
- import-json: runtime JSON -> SQLite
- export-json: SQLite -> runtime JSON
- check-nearby: report near-coordinate pairs (including different names)

The static app keeps reading JSON files, but those JSON files are generated
distribution artifacts from the business-owned DB.
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
RUNTIME_DATA_DIR = REPO_ROOT / "platform" / "system" / "runtime" / "data" / "kabukicho"
DB_PATH = APP_DIR / "data" / "kabukicho_poi.db"
NEARBY_REPORT_PATH = APP_DIR / "nearby_coordinate_report.json"

CATEGORY_FILES = (
    "toilet.json",
    "smoking.json",
    "convenience.json",
    "atm.json",
    "coin_locker.json",
    "lodging.json",
)


ALLOWED_HARD_DUPLICATE_PAIRS = {
    frozenset(
        {
            ("atm.json", "イオン銀行ATM(ミニストップ新宿歌舞伎町店・2号機)"),
            ("atm.json", "みずほ銀行ATM(ミニストップ新宿歌舞伎町店・1号機)"),
        }
    ),
    frozenset(
        {
            ("coin_locker.json", "東急歌舞伎町タワー地下1階コインロッカー"),
            ("coin_locker.json", "東急歌舞伎町タワー4階シネマフロアロッカー"),
        }
    ),
    frozenset(
        {
            ("coin_locker.json", "東急歌舞伎町タワー地下1階コインロッカー"),
            ("coin_locker.json", "東急歌舞伎町タワー10階(109シネマズプレミアム新宿)ロッカー"),
        }
    ),
    frozenset(
        {
            ("coin_locker.json", "東急歌舞伎町タワー4階シネマフロアロッカー"),
            ("coin_locker.json", "東急歌舞伎町タワー10階(109シネマズプレミアム新宿)ロッカー"),
        }
    ),
    frozenset(
        {
            ("toilet.json", "東急歌舞伎町タワー トイレ"),
            ("toilet.json", "東急歌舞伎町タワー 2階トイレ"),
        }
    ),
}

KNOWN_KEYS = {
    "name",
    "lat",
    "lng",
    "description",
    "category",
    "tags",
    "last_updated",
    "reliability_score",
    "source_type",
    "type",
    "verification_method",
    "gray_zone_note",
    "licensed_as",
}


@dataclass
class Poi:
    poi_id: int
    file_name: str
    sort_order: int
    name: str
    category: str
    lat: float
    lng: float


def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS pois (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          file_name TEXT NOT NULL,
          sort_order INTEGER NOT NULL,
          name TEXT NOT NULL,
          lat REAL NOT NULL,
          lng REAL NOT NULL,
          description TEXT NOT NULL,
          category TEXT NOT NULL,
          last_updated TEXT,
          reliability_score INTEGER,
          source_type TEXT,
          type TEXT,
          verification_method TEXT,
          gray_zone_note TEXT,
          licensed_as TEXT,
          extra_json TEXT NOT NULL DEFAULT '{}',
          UNIQUE(file_name, sort_order)
        );

        CREATE TABLE IF NOT EXISTS poi_tags (
          poi_id INTEGER NOT NULL,
          tag_order INTEGER NOT NULL,
          tag TEXT NOT NULL,
          PRIMARY KEY (poi_id, tag_order),
          FOREIGN KEY (poi_id) REFERENCES pois(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_pois_category_lat_lng
          ON pois(category, lat, lng);
        """
    )


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000.0
    p = math.pi / 180.0
    dlat = (lat2 - lat1) * p
    dlng = (lng2 - lng1) * p
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlng / 2) ** 2
    return r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def import_json(conn: sqlite3.Connection) -> None:
    ensure_schema(conn)
    conn.execute("DELETE FROM poi_tags")
    conn.execute("DELETE FROM pois")

    for file_name in CATEGORY_FILES:
        path = RUNTIME_DATA_DIR / file_name
        entries = json.loads(path.read_text(encoding="utf-8"))
        for idx, entry in enumerate(entries):
            tags = entry.get("tags") or []
            extra = {k: v for k, v in entry.items() if k not in KNOWN_KEYS}
            cur = conn.execute(
                """
                INSERT INTO pois (
                  file_name, sort_order, name, lat, lng, description, category,
                  last_updated, reliability_score, source_type, type,
                  verification_method, gray_zone_note, licensed_as, extra_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_name,
                    idx,
                    entry.get("name", ""),
                    float(entry.get("lat")),
                    float(entry.get("lng")),
                    entry.get("description", ""),
                    entry.get("category", ""),
                    entry.get("last_updated"),
                    entry.get("reliability_score"),
                    entry.get("source_type"),
                    entry.get("type"),
                    entry.get("verification_method"),
                    entry.get("gray_zone_note"),
                    entry.get("licensed_as"),
                    json.dumps(extra, ensure_ascii=False),
                ),
            )
            poi_id = int(cur.lastrowid)
            for tag_idx, tag in enumerate(tags):
                conn.execute(
                    "INSERT INTO poi_tags (poi_id, tag_order, tag) VALUES (?, ?, ?)",
                    (poi_id, tag_idx, str(tag)),
                )

    conn.commit()


def export_json(conn: sqlite3.Connection) -> None:
    ensure_schema(conn)

    row_count = conn.execute("SELECT COUNT(*) AS c FROM pois").fetchone()["c"]
    if row_count == 0:
        import_json(conn)

    RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for file_name in CATEGORY_FILES:
        rows = conn.execute(
            """
            SELECT * FROM pois
            WHERE file_name = ?
            ORDER BY sort_order ASC, id ASC
            """,
            (file_name,),
        ).fetchall()
        out = []
        for row in rows:
            tags = [
                r["tag"]
                for r in conn.execute(
                    "SELECT tag FROM poi_tags WHERE poi_id = ? ORDER BY tag_order ASC",
                    (row["id"],),
                ).fetchall()
            ]
            entry = {
                "name": row["name"],
                "lat": row["lat"],
                "lng": row["lng"],
                "description": row["description"],
                "category": row["category"],
                "tags": tags,
                "last_updated": row["last_updated"],
                "reliability_score": row["reliability_score"],
                "source_type": row["source_type"],
                "type": row["type"],
            }
            if row["verification_method"] is not None:
                entry["verification_method"] = row["verification_method"]
            if row["gray_zone_note"] is not None:
                entry["gray_zone_note"] = row["gray_zone_note"]
            if row["licensed_as"] is not None:
                entry["licensed_as"] = row["licensed_as"]

            extra = json.loads(row["extra_json"] or "{}")
            entry.update(extra)
            out.append(entry)

        (RUNTIME_DATA_DIR / file_name).write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def fetch_pois(conn: sqlite3.Connection) -> list[Poi]:
    rows = conn.execute(
        "SELECT id, file_name, sort_order, name, category, lat, lng FROM pois ORDER BY file_name, sort_order"
    ).fetchall()
    return [
        Poi(
            poi_id=row["id"],
            file_name=row["file_name"],
            sort_order=row["sort_order"],
            name=row["name"],
            category=row["category"],
            lat=float(row["lat"]),
            lng=float(row["lng"]),
        )
        for row in rows
    ]


def check_nearby(
    conn: sqlite3.Connection,
    threshold_m: float,
    hard_m: float,
    output_path: Path,
    similar_name_threshold: float,
    similar_name_radius_m: float,
    max_hard_duplicates: int | None,
    max_alias_candidates: int | None,
) -> None:
    ensure_schema(conn)
    row_count = conn.execute("SELECT COUNT(*) AS c FROM pois").fetchone()["c"]
    if row_count == 0:
        import_json(conn)

    pois = fetch_pois(conn)
    nearby_pairs = []
    same_name_far_pairs = []

    for i in range(len(pois)):
        a = pois[i]
        for j in range(i + 1, len(pois)):
            b = pois[j]
            dist = haversine_m(a.lat, a.lng, b.lat, b.lng)
            name_ratio = SequenceMatcher(None, a.name, b.name).ratio()

            similar_name_near = (
                a.category == b.category
                and name_ratio >= similar_name_threshold
                and dist <= similar_name_radius_m
            )

            if dist <= threshold_m or similar_name_near:
                severity = "review"
                if a.category == b.category and dist <= hard_m:
                    severity = "hard_duplicate"
                    pair_key = frozenset({(a.file_name, a.name), (b.file_name, b.name)})
                    if pair_key in ALLOWED_HARD_DUPLICATE_PAIRS:
                        severity = "allowed_hard_duplicate"
                elif similar_name_near and dist > threshold_m:
                    severity = "same_category_name_alias_candidate"
                nearby_pairs.append(
                    {
                        "severity": severity,
                        "distance_m": round(dist, 2),
                        "name_similarity": round(name_ratio, 3),
                        "a": {
                            "file": a.file_name,
                            "index": a.sort_order,
                            "name": a.name,
                            "category": a.category,
                            "lat": a.lat,
                            "lng": a.lng,
                        },
                        "b": {
                            "file": b.file_name,
                            "index": b.sort_order,
                            "name": b.name,
                            "category": b.category,
                            "lat": b.lat,
                            "lng": b.lng,
                        },
                    }
                )

            # Additional visibility: similar names even when not near enough.
            if a.category == b.category and name_ratio >= 0.72 and dist > threshold_m:
                same_name_far_pairs.append(
                    {
                        "distance_m": round(dist, 2),
                        "name_similarity": round(name_ratio, 3),
                        "a": {"file": a.file_name, "index": a.sort_order, "name": a.name},
                        "b": {"file": b.file_name, "index": b.sort_order, "name": b.name},
                    }
                )

    nearby_pairs.sort(key=lambda x: x["distance_m"])
    same_name_far_pairs.sort(key=lambda x: (-x["name_similarity"], x["distance_m"]))

    report = {
        "threshold_m": threshold_m,
        "hard_duplicate_m": hard_m,
        "similar_name_threshold": similar_name_threshold,
        "similar_name_radius_m": similar_name_radius_m,
        "db_path": str(DB_PATH),
        "poi_count": len(pois),
        "nearby_pair_count": len(nearby_pairs),
        "hard_duplicate_count": sum(1 for p in nearby_pairs if p["severity"] == "hard_duplicate"),
        "allowed_hard_duplicate_count": sum(1 for p in nearby_pairs if p["severity"] == "allowed_hard_duplicate"),
        "nearby_pairs": nearby_pairs,
        "name_similar_but_far_pairs": same_name_far_pairs,
    }
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"report: {output_path}")
    print(f"poi_count: {len(pois)}")
    print(f"nearby_pair_count: {len(nearby_pairs)}")
    print(f"hard_duplicate_count: {report['hard_duplicate_count']}")
    print(f"allowed_hard_duplicate_count: {report['allowed_hard_duplicate_count']}")

    if max_hard_duplicates is not None and report["hard_duplicate_count"] > max_hard_duplicates:
        raise RuntimeError(
            "hard_duplicate_count exceeds threshold: "
            f"{report['hard_duplicate_count']} > {max_hard_duplicates}"
        )

    alias_candidate_count = sum(1 for p in nearby_pairs if p["severity"] == "same_category_name_alias_candidate")
    if max_alias_candidates is not None and alias_candidate_count > max_alias_candidates:
        raise RuntimeError(
            "same_category_name_alias_candidate count exceeds threshold: "
            f"{alias_candidate_count} > {max_alias_candidates}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("import-json", help="Import runtime JSON data into SQLite (DB becomes canonical)")
    sub.add_parser("export-json", help="Export SQLite data to runtime JSON files")

    check = sub.add_parser("check-nearby", help="Check near-coordinate facilities even with different names")
    check.add_argument("--threshold-m", type=float, default=35.0)
    check.add_argument("--hard-m", type=float, default=8.0)
    check.add_argument("--similar-name-threshold", type=float, default=0.64)
    check.add_argument("--similar-name-radius-m", type=float, default=140.0)
    check.add_argument("--output", type=Path, default=NEARBY_REPORT_PATH)
    check.add_argument("--max-hard-duplicates", type=int, default=None)
    check.add_argument("--max-alias-candidates", type=int, default=None)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    conn = connect_db()
    try:
        if args.cmd == "import-json":
            import_json(conn)
            print(f"db: {DB_PATH}")
            print("imported: yes")
            return 0

        if args.cmd == "export-json":
            export_json(conn)
            print("exported: yes")
            return 0

        if args.cmd == "check-nearby":
            check_nearby(
                conn,
                args.threshold_m,
                args.hard_m,
                args.output,
                args.similar_name_threshold,
                args.similar_name_radius_m,
                args.max_hard_duplicates,
                args.max_alias_candidates,
            )
            return 0

        raise RuntimeError(f"Unknown command: {args.cmd}")
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
