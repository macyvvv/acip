"""SQLite storage for cf_gb_relative_system's store data.

One shared database (`data/stores.db`) with `area_id` as a column, not one
file per area -- see artifacts/census-pivot-2026-07-21/WBS.md section 2 for
the reasoning (cross-area queries, single backup/restore surface). Stdlib
`sqlite3` only, no ORM, matching this business's "no third-party runtime
dependencies" discipline and the sibling kabukicho_survival_map business's
own `poi_db_sync.py` precedent.

Schema:
  areas             -- one row per area/station (e.g. 'ueno')
  stores            -- the census row: cheap, required at discovery time
  store_enrichment  -- 1:1 optional sidecar; ABSENCE of a row is the
                       "no enrichment data yet" state, not a null-filled row
  store_sns         -- 1:N, independent of enrichment completeness
  store_change_log  -- append-only, generalizes store-artifact.json's
                       per-record change_log into one shared table
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

TOOL_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = TOOL_ROOT / "data" / "stores.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS areas (
    area_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    line_hint TEXT
);

CREATE TABLE IF NOT EXISTS stores (
    store_id TEXT PRIMARY KEY,
    area_id TEXT NOT NULL REFERENCES areas(area_id),
    name_raw TEXT NOT NULL,
    name_normalized TEXT,
    store_type TEXT NOT NULL DEFAULT 'unknown',
    discovery_method TEXT NOT NULL,
    discovered_at TEXT NOT NULL,
    existence_confidence TEXT NOT NULL DEFAULT 'probable',
    status TEXT NOT NULL DEFAULT 'unknown',
    completeness_tier TEXT NOT NULL DEFAULT 'known',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS store_enrichment (
    store_id TEXT PRIMARY KEY REFERENCES stores(store_id),
    address TEXT,
    lat REAL,
    lng REAL,
    coordinate_source TEXT,
    coordinate_precision TEXT,
    official_url TEXT,
    phone TEXT,
    concept_theme TEXT,
    hours_json TEXT,
    pricing_model TEXT,
    price_items_json TEXT,
    price_unavailable_reason TEXT,
    cast_headcount INTEGER,
    reliability_score INTEGER,
    verification_method TEXT,
    last_verified_at TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS store_sns (
    store_id TEXT NOT NULL REFERENCES stores(store_id),
    platform TEXT NOT NULL,
    url TEXT NOT NULL,
    PRIMARY KEY (store_id, platform)
);

CREATE TABLE IF NOT EXISTS store_change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id TEXT NOT NULL REFERENCES stores(store_id),
    changed_at TEXT NOT NULL,
    field TEXT NOT NULL,
    previous_value TEXT,
    new_value TEXT,
    change_type TEXT NOT NULL,
    source_url TEXT,
    source_artifact_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_stores_area ON stores(area_id);
CREATE INDEX IF NOT EXISTS idx_change_log_store ON store_change_log(store_id);
"""


def connect_db(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Columns added after the table's initial CREATE -- "CREATE TABLE IF NOT
# EXISTS" alone is a no-op against an already-existing table from an older
# run, so a new column needs its own idempotent ALTER TABLE here.
_COLUMN_MIGRATIONS = (
    ("store_enrichment", "concept_theme", "TEXT"),
)


def _apply_column_migrations(conn: sqlite3.Connection) -> None:
    for table, column, column_type in _COLUMN_MIGRATIONS:
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        if column not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)
    _apply_column_migrations(conn)
    conn.commit()


@contextmanager
def open_db(db_path: Path | str = DEFAULT_DB_PATH) -> Iterator[sqlite3.Connection]:
    """Connect, ensure schema, yield a connection, commit-or-rollback on exit."""
    conn = connect_db(db_path)
    try:
        ensure_schema(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_area(conn: sqlite3.Connection, area_id: str, display_name: str, line_hint: str | None = None) -> None:
    conn.execute(
        "INSERT INTO areas (area_id, display_name, line_hint) VALUES (?, ?, ?) "
        "ON CONFLICT(area_id) DO UPDATE SET display_name = excluded.display_name, line_hint = excluded.line_hint",
        (area_id, display_name, line_hint),
    )
