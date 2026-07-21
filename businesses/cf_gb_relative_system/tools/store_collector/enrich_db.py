"""DB-backed enrichment layer on top of collect.py's fetch+extract pipeline.

Maps a fetch onto an EXISTING census row (census.py must have run for this
store_id first) rather than creating standalone drafts -- this keeps the
census-before-depth ordering the whole pivot is about; enrich_store_from_url
raises if the store_id has no census row.

Two tiers this module can produce:
  has_official_source -- automatic, from a successful fetch. Only
                          official_url and a confidently-extracted phone
                          are written; everything else stays NULL/unset,
                          same "never auto-set verification_method" rule
                          collect.py already enforces.
  verified            -- confirm_verified_fields() only, never called
                          automatically. A human (or an LLM reviewing the
                          cached raw HTML + needs_review list) must supply
                          every field explicitly.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import collect
import db


def enrich_store_from_url(
    conn,
    store_id: str,
    url: str,
    cache_root: Path | None = None,
    fetcher: collect.Fetcher = collect.default_fetcher,
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    timestamp = now.isoformat().replace("+00:00", "Z")
    cache_root = cache_root or (collect.TOOL_ROOT / "cache")

    existing = conn.execute(
        "SELECT store_id, completeness_tier FROM stores WHERE store_id = ?", (store_id,)
    ).fetchone()
    if existing is None:
        raise ValueError(f"{store_id!r} has no census row -- run census.py before enrich_db.py")

    record = collect.fetch_and_cache(url, store_id, cache_root, fetcher=fetcher, now=now)
    if record["outcome"] != "success":
        return {"store_id": store_id, "outcome": record["outcome"]}

    html = Path(record["raw_path"]).read_text(encoding="utf-8")
    draft = collect.draft_store_artifact(store_id, url, html, record["attempted_at"])
    phone = draft.get("phone")

    conn.execute(
        "INSERT INTO store_enrichment (store_id, official_url, phone, updated_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(store_id) DO UPDATE SET official_url = excluded.official_url, "
        "phone = COALESCE(excluded.phone, store_enrichment.phone), updated_at = excluded.updated_at",
        (store_id, url, phone, timestamp),
    )
    if existing["completeness_tier"] == "known":
        conn.execute(
            "UPDATE stores SET completeness_tier = 'has_official_source', updated_at = ? WHERE store_id = ?",
            (timestamp, store_id),
        )
    conn.execute(
        "INSERT INTO store_change_log (store_id, changed_at, field, previous_value, new_value, "
        "change_type, source_url) VALUES (?, ?, 'official_url', NULL, ?, 'url_change', ?)",
        (store_id, timestamp, url, url),
    )

    return {
        "store_id": store_id,
        "outcome": "has_official_source",
        "needs_review": draft["needs_review"],
        "draft_path": str(cache_root / f"{store_id}.draft.json"),
    }


def confirm_verified_fields(
    conn,
    store_id: str,
    *,
    address: str,
    hours: list[dict],
    pricing_model: str,
    price_items: list[dict],
    verification_method: str,
    reliability_score: int,
    source_url: str,
    now: datetime | None = None,
) -> None:
    """Human/LLM-confirmed promotion to completeness_tier='verified'.

    Never called automatically by census.py or enrich_store_from_url --
    every argument here represents a fact a reviewer explicitly confirmed
    against the store's own official source, not a machine guess."""
    now = now or datetime.now(timezone.utc)
    timestamp = now.isoformat().replace("+00:00", "Z")

    existing = conn.execute("SELECT store_id FROM stores WHERE store_id = ?", (store_id,)).fetchone()
    if existing is None:
        raise ValueError(f"{store_id!r} has no census row")

    conn.execute(
        "INSERT INTO store_enrichment (store_id, address, hours_json, pricing_model, price_items_json, "
        "verification_method, reliability_score, last_verified_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(store_id) DO UPDATE SET address=excluded.address, hours_json=excluded.hours_json, "
        "pricing_model=excluded.pricing_model, price_items_json=excluded.price_items_json, "
        "verification_method=excluded.verification_method, reliability_score=excluded.reliability_score, "
        "last_verified_at=excluded.last_verified_at, updated_at=excluded.updated_at",
        (
            store_id,
            address,
            json.dumps(hours, ensure_ascii=False),
            pricing_model,
            json.dumps(price_items, ensure_ascii=False),
            verification_method,
            reliability_score,
            timestamp,
            timestamp,
        ),
    )
    conn.execute(
        "UPDATE stores SET completeness_tier = 'verified', updated_at = ? WHERE store_id = ?",
        (timestamp, store_id),
    )
    conn.execute(
        "INSERT INTO store_change_log (store_id, changed_at, field, previous_value, new_value, "
        "change_type, source_url) VALUES (?, ?, 'completeness_tier', NULL, 'verified', 'correction', ?)",
        (store_id, timestamp, source_url),
    )
