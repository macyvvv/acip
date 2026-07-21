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
