"""Breadth-first store census: record that a store exists, nothing more.

Ingests a per-area name-list JSON (compiled by a human/LLM web-search pass
-- see the sourcing conditions in artifacts/S-011/source-register.json's
`search-engine-discovery` entry, amended 2026-07-21: varied general search
queries only, never by systematically paging one aggregator's full area
listing) and inserts `stores` rows at completeness_tier='known'. This is
deliberately separate from collect.py/collect_batch.py: census never
requires or checks a source URL against the deny list, because it never
fetches anything -- names come from search result text the operator/LLM
already read, not from an automated request this tool makes.

Input shape (one file per area):
    [{"name_raw": "...", "existence_confidence": "confirmed_exists"|"probable"|"unconfirmed",
      "discovery_note": "...", "store_type": "concept_cafe"|"girls_bar"}, ...]

`store_type` is optional -- omit it (defaults to "unknown") when the
search results genuinely don't make it clear yet; set it whenever it's
already obvious from which query/listing surfaced the name (a
"ガールズバー" search result is a girls_bar) rather than leaving a fact
you already have sitting unrecorded. See enrich_db.update_store_category()
to set/correct store_type and concept_theme (e.g. "魔法学園", "水着",
"うさぎ") later, independent of official-source enrichment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import db

TOOL_ROOT = Path(__file__).resolve().parent

_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")


def slugify_store_id(name_raw: str, area_id: str) -> str:
    """Deterministic slug: same (name_raw, area_id) must produce the same
    store_id in every process, every run, forever -- it's the DB primary
    key and the join target every enrichment call looks up by. Python's
    builtin hash() is salted per-process (PYTHONHASHSEED) specifically to
    prevent this kind of stability; using it here was a real bug -- a
    Japanese-only name got a different store_id on every fresh run, and a
    later enrich_db call against the "same" store_id from an earlier run
    would raise "has no census row" even though the store really was
    censused. Use hashlib.sha256 (always deterministic) instead."""
    normalized = unicodedata.normalize("NFKC", name_raw).lower()
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    if ascii_only.strip():
        slug_source = ascii_only
    else:
        slug_source = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    slug = _SLUG_STRIP_RE.sub("-", slug_source).strip("-") or "store"
    return f"{area_id}-{slug}"[:120]


def ingest_area_census(
    conn,
    area_id: str,
    area_display_name: str,
    candidates: list[dict],
    now: datetime | None = None,
) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    timestamp = now.isoformat().replace("+00:00", "Z")
    db.ensure_area(conn, area_id, area_display_name)

    results = []
    for candidate in candidates:
        name_raw = candidate["name_raw"]
        store_id = slugify_store_id(name_raw, area_id)
        existing = conn.execute("SELECT store_id FROM stores WHERE store_id = ?", (store_id,)).fetchone()
        if existing:
            results.append({"store_id": store_id, "name_raw": name_raw, "outcome": "already_known"})
            continue

        conn.execute(
            "INSERT INTO stores (store_id, area_id, name_raw, store_type, discovery_method, discovered_at, "
            "existence_confidence, status, completeness_tier, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 'unknown', 'known', ?, ?)",
            (
                store_id,
                area_id,
                name_raw,
                candidate.get("store_type", "unknown"),
                candidate.get("discovery_method", "web-search"),
                timestamp,
                candidate.get("existence_confidence", "probable"),
                timestamp,
                timestamp,
            ),
        )
        conn.execute(
            "INSERT INTO store_change_log (store_id, changed_at, field, previous_value, new_value, "
            "change_type, source_url) VALUES (?, ?, 'completeness_tier', NULL, 'known', 'initial_capture', ?)",
            (store_id, timestamp, candidate.get("discovery_note", "web-search: varied queries")),
        )
        results.append({"store_id": store_id, "name_raw": name_raw, "outcome": "inserted"})

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest a per-area name-list census into stores.db.")
    parser.add_argument("area_id", help="Stable area slug, e.g. ueno")
    parser.add_argument("area_display_name", help="Human-readable area label, e.g. 上野")
    parser.add_argument("candidates", type=Path, help="JSON file: [{name_raw, existence_confidence, discovery_note}, ...]")
    parser.add_argument("--db-path", type=Path, default=db.DEFAULT_DB_PATH)
    args = parser.parse_args(argv)

    candidates = json.loads(args.candidates.read_text(encoding="utf-8"))
    with db.open_db(args.db_path) as conn:
        results = ingest_area_census(conn, args.area_id, args.area_display_name, candidates)

    inserted = sum(1 for r in results if r["outcome"] == "inserted")
    print(f"inserted={inserted} already_known={len(results) - inserted} total={len(results)}")
    for r in results:
        print(f"  {r['outcome']:14s} {r['store_id']:40s} {r['name_raw']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
