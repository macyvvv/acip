from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import db  # noqa: E402


def test_ensure_schema_is_idempotent() -> None:
    conn = db.connect_db(":memory:")
    db.ensure_schema(conn)
    db.ensure_schema(conn)  # must not raise on a second call

    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"areas", "stores", "store_enrichment", "store_sns", "store_change_log"} <= tables


def test_foreign_keys_are_enforced() -> None:
    conn = db.connect_db(":memory:")
    db.ensure_schema(conn)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO stores (store_id, area_id, name_raw, discovery_method, discovered_at, created_at, updated_at) "
            "VALUES ('x', 'nonexistent-area', 'X', 'web-search', 't', 't', 't')"
        )
        conn.commit()


def test_ensure_area_upserts(tmp_path: Path) -> None:
    with db.open_db(tmp_path / "test.db") as conn:
        db.ensure_area(conn, "ueno", "上野")
        db.ensure_area(conn, "ueno", "上野 (updated)")

    with db.open_db(tmp_path / "test.db") as conn:
        rows = conn.execute("SELECT * FROM areas").fetchall()
        assert len(rows) == 1
        assert rows[0]["display_name"] == "上野 (updated)"


def test_open_db_commits_on_success_and_creates_file(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "stores.db"
    with db.open_db(db_path) as conn:
        db.ensure_area(conn, "ueno", "上野")

    assert db_path.exists()
    with db.open_db(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM areas").fetchone()[0] == 1


def test_open_db_rolls_back_on_exception(tmp_path: Path) -> None:
    db_path = tmp_path / "stores.db"
    try:
        with db.open_db(db_path) as conn:
            db.ensure_area(conn, "ueno", "上野")
            raise RuntimeError("simulated failure mid-transaction")
    except RuntimeError:
        pass

    with db.open_db(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM areas").fetchone()[0] == 0


def test_column_migration_adds_concept_theme_to_pre_existing_table(tmp_path: Path) -> None:
    # Simulate a DB created before concept_theme existed: build
    # store_enrichment without it, then confirm ensure_schema() (which a
    # real re-run always calls) adds it without losing existing data.
    db_path = tmp_path / "stores.db"
    conn = db.connect_db(db_path)
    conn.executescript(
        """
        CREATE TABLE areas (area_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, line_hint TEXT);
        CREATE TABLE stores (
            store_id TEXT PRIMARY KEY, area_id TEXT NOT NULL, name_raw TEXT NOT NULL,
            store_type TEXT NOT NULL DEFAULT 'unknown', discovery_method TEXT NOT NULL,
            discovered_at TEXT NOT NULL, existence_confidence TEXT NOT NULL DEFAULT 'probable',
            status TEXT NOT NULL DEFAULT 'unknown', completeness_tier TEXT NOT NULL DEFAULT 'known',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE store_enrichment (
            store_id TEXT PRIMARY KEY, official_url TEXT, phone TEXT, updated_at TEXT NOT NULL
        );
        """
    )
    conn.execute(
        "INSERT INTO areas VALUES ('ueno', '上野', NULL)"
    )
    conn.execute(
        "INSERT INTO stores VALUES ('ueno-x', 'ueno', 'X', 'unknown', 'web-search', 't', 'probable', 'unknown', 'known', 't', 't')"
    )
    conn.execute("INSERT INTO store_enrichment (store_id, official_url, phone, updated_at) VALUES ('ueno-x', 'https://x.invalid', NULL, 't')")
    conn.commit()
    conn.close()

    conn = db.connect_db(db_path)
    db.ensure_schema(conn)  # must not raise, must not drop the existing row

    columns = {row["name"] for row in conn.execute("PRAGMA table_info(store_enrichment)")}
    assert "concept_theme" in columns

    row = conn.execute("SELECT official_url, concept_theme FROM store_enrichment WHERE store_id = 'ueno-x'").fetchone()
    assert row["official_url"] == "https://x.invalid"
    assert row["concept_theme"] is None
