from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import census  # noqa: E402
import db  # noqa: E402


def test_slugify_is_stable_and_area_scoped() -> None:
    a = census.slugify_store_id("Example Store", "ueno")
    b = census.slugify_store_id("Example Store", "ueno")
    c = census.slugify_store_id("Example Store", "shinjuku")

    assert a == b
    assert a != c
    assert a.startswith("ueno-")


def test_slugify_handles_japanese_only_names() -> None:
    slug = census.slugify_store_id("のわ", "ueno")
    assert slug.startswith("ueno-")
    assert slug != "ueno-"


def test_ingest_creates_known_tier_rows() -> None:
    conn = db.connect_db(":memory:")
    db.ensure_schema(conn)
    now = datetime(2026, 7, 21, tzinfo=timezone.utc)

    results = census.ingest_area_census(
        conn,
        "ueno",
        "上野",
        [
            {"name_raw": "esora", "existence_confidence": "confirmed_exists"},
            {"name_raw": "のわ", "existence_confidence": "probable"},
        ],
        now=now,
    )

    assert {r["outcome"] for r in results} == {"inserted"}
    rows = conn.execute("SELECT store_id, completeness_tier, status, existence_confidence FROM stores").fetchall()
    assert len(rows) == 2
    for row in rows:
        assert row["completeness_tier"] == "known"
        assert row["status"] == "unknown"

    esora = conn.execute("SELECT * FROM stores WHERE name_raw = 'esora'").fetchone()
    assert esora["existence_confidence"] == "confirmed_exists"


def test_ingest_is_idempotent_on_rerun() -> None:
    conn = db.connect_db(":memory:")
    db.ensure_schema(conn)
    candidates = [{"name_raw": "esora"}]

    first = census.ingest_area_census(conn, "ueno", "上野", candidates)
    second = census.ingest_area_census(conn, "ueno", "上野", candidates)

    assert first[0]["outcome"] == "inserted"
    assert second[0]["outcome"] == "already_known"
    assert conn.execute("SELECT COUNT(*) FROM stores").fetchone()[0] == 1


def test_ingest_writes_initial_capture_change_log_entry() -> None:
    conn = db.connect_db(":memory:")
    db.ensure_schema(conn)

    census.ingest_area_census(conn, "ueno", "上野", [{"name_raw": "esora"}])

    log = conn.execute("SELECT * FROM store_change_log").fetchall()
    assert len(log) == 1
    assert log[0]["change_type"] == "initial_capture"
    assert log[0]["new_value"] == "known"


def test_two_areas_do_not_collide(tmp_path: Path) -> None:
    with db.open_db(tmp_path / "stores.db") as conn:
        census.ingest_area_census(conn, "ueno", "上野", [{"name_raw": "Same Name"}])
        census.ingest_area_census(conn, "shinjuku", "新宿", [{"name_raw": "Same Name"}])

    with db.open_db(tmp_path / "stores.db") as conn:
        rows = conn.execute("SELECT store_id, area_id FROM stores ORDER BY area_id").fetchall()
        assert len(rows) == 2
        assert {row["area_id"] for row in rows} == {"ueno", "shinjuku"}
