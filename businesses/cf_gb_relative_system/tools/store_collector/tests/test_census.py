from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import census  # noqa: E402
import db  # noqa: E402

TOOL_ROOT = Path(__file__).resolve().parents[1]


def test_slugify_is_stable_and_area_scoped() -> None:
    a = census.slugify_store_id("Example Store", "ueno")
    b = census.slugify_store_id("Example Store", "ueno")
    c = census.slugify_store_id("Example Store", "shinjuku")

    assert a == b
    assert a != c
    assert a.startswith("ueno-")


def test_slugify_of_japanese_only_name_is_stable_across_processes() -> None:
    # Regression: the original implementation fell back to Python's
    # builtin hash() for names with no ASCII characters at all (e.g.
    # "うさぎだから"), which is salted per-process by design
    # (PYTHONHASHSEED) -- the real Ueno run produced a different store_id
    # every time the script was re-invoked as a fresh process, so a later
    # enrich_db call against the store_id from an earlier run failed with
    # "has no census row" even though the store really had been censused.
    # A single pytest process can't observe this (hash() is stable within
    # one process), so this must be checked across two real subprocesses.
    script = (
        "import sys; sys.path.insert(0, %r); import census; "
        "print(census.slugify_store_id('うさぎだから', 'ueno'))" % str(TOOL_ROOT)
    )
    first = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
    second = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)

    assert first.stdout.strip() == second.stdout.strip()
    assert first.stdout.strip().startswith("ueno-")


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


def test_ingest_defaults_store_type_to_unknown_when_not_given() -> None:
    conn = db.connect_db(":memory:")
    db.ensure_schema(conn)

    census.ingest_area_census(conn, "ueno", "上野", [{"name_raw": "esora"}])

    row = conn.execute("SELECT store_type FROM stores WHERE name_raw = 'esora'").fetchone()
    assert row["store_type"] == "unknown"


def test_ingest_records_store_type_when_already_known_from_search_context() -> None:
    # Regression: every store from the real Ueno/Okachimachi/Yushima runs
    # ended up store_type='unknown' even though most were discovered via a
    # query that already said which one (e.g. "ガールズバー") -- the field
    # was known but never recorded. census.py must accept it when given.
    conn = db.connect_db(":memory:")
    db.ensure_schema(conn)

    census.ingest_area_census(
        conn,
        "ueno",
        "上野",
        [{"name_raw": "Noisy Cats", "store_type": "girls_bar"}],
    )

    row = conn.execute("SELECT store_type FROM stores WHERE name_raw = 'Noisy Cats'").fetchone()
    assert row["store_type"] == "girls_bar"


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
