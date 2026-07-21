from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

import census  # noqa: E402
import collect  # noqa: E402
import db  # noqa: E402
import enrich_db  # noqa: E402


FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures"


def _fake_fetcher(status: int = 200, fixture: str = "clean_store_page.html"):
    body = (FIXTURES / fixture).read_text(encoding="utf-8")

    def fetcher(url: str, user_agent: str) -> collect.FetchResult:
        return collect.FetchResult(url=url, status=status, body=body)

    return fetcher


def _censused_db(tmp_path: Path):
    conn = db.connect_db(tmp_path / "stores.db")
    db.ensure_schema(conn)
    census.ingest_area_census(conn, "ueno", "上野", [{"name_raw": "Example Store"}])
    conn.commit()
    store_id = conn.execute("SELECT store_id FROM stores LIMIT 1").fetchone()["store_id"]
    return conn, store_id


def test_enrich_requires_an_existing_census_row(tmp_path: Path) -> None:
    conn = db.connect_db(tmp_path / "stores.db")
    db.ensure_schema(conn)

    with pytest.raises(ValueError, match="no census row"):
        enrich_db.enrich_store_from_url(
            conn, "nonexistent", "https://example-store.invalid/",
            cache_root=tmp_path / "cache", fetcher=_fake_fetcher(),
        )


def test_successful_enrich_promotes_tier_to_has_official_source(tmp_path: Path) -> None:
    conn, store_id = _censused_db(tmp_path)

    result = enrich_db.enrich_store_from_url(
        conn, store_id, "https://example-store.invalid/",
        cache_root=tmp_path / "cache", fetcher=_fake_fetcher(),
    )

    assert result["outcome"] == "has_official_source"
    row = conn.execute("SELECT completeness_tier FROM stores WHERE store_id = ?", (store_id,)).fetchone()
    assert row["completeness_tier"] == "has_official_source"

    enrichment = conn.execute("SELECT official_url, phone FROM store_enrichment WHERE store_id = ?", (store_id,)).fetchone()
    assert enrichment["official_url"] == "https://example-store.invalid/"
    assert enrichment["phone"] == "03-1234-5678"


def test_successful_enrich_writes_discovered_sns_links(tmp_path: Path) -> None:
    # Regression: store_sns stayed empty in the real Ueno run even though
    # 3 of 4 fetched pages had real SNS links -- extract_fields() never
    # looked for them, so nothing ever reached this table.
    conn, store_id = _censused_db(tmp_path)

    result = enrich_db.enrich_store_from_url(
        conn, store_id, "https://example-store.invalid/",
        cache_root=tmp_path / "cache", fetcher=_fake_fetcher(fixture="sns_links_page.html"),
    )

    assert {entry["platform"] for entry in result["sns_urls"]} == {"x", "instagram", "line"}

    rows = conn.execute("SELECT platform, url FROM store_sns WHERE store_id = ? ORDER BY platform", (store_id,)).fetchall()
    assert [row["platform"] for row in rows] == ["instagram", "line", "x"]

    log_types = [
        row["field"]
        for row in conn.execute("SELECT field FROM store_change_log WHERE store_id = ?", (store_id,))
    ]
    assert "sns_urls" in log_types


def test_enrich_without_sns_links_writes_no_store_sns_rows(tmp_path: Path) -> None:
    conn, store_id = _censused_db(tmp_path)

    result = enrich_db.enrich_store_from_url(
        conn, store_id, "https://example-store.invalid/",
        cache_root=tmp_path / "cache", fetcher=_fake_fetcher(),  # clean_store_page.html, no SNS links
    )

    assert result["sns_urls"] == []
    assert conn.execute("SELECT COUNT(*) FROM store_sns WHERE store_id = ?", (store_id,)).fetchone()[0] == 0


def test_failed_fetch_does_not_touch_tier_or_write_enrichment(tmp_path: Path) -> None:
    conn, store_id = _censused_db(tmp_path)

    def failing_fetcher(url: str, user_agent: str) -> collect.FetchResult:
        raise TimeoutError("simulated")

    with pytest.raises(TimeoutError):
        enrich_db.enrich_store_from_url(
            conn, store_id, "https://example-store.invalid/",
            cache_root=tmp_path / "cache", fetcher=failing_fetcher,
        )

    row = conn.execute("SELECT completeness_tier FROM stores WHERE store_id = ?", (store_id,)).fetchone()
    assert row["completeness_tier"] == "known"
    assert conn.execute("SELECT COUNT(*) FROM store_enrichment").fetchone()[0] == 0


def test_denied_url_never_writes_to_db(tmp_path: Path) -> None:
    conn, store_id = _censused_db(tmp_path)

    with pytest.raises(collect.SourceDenied):
        enrich_db.enrich_store_from_url(
            conn, store_id, "https://www.pokepara.jp/some/store",
            cache_root=tmp_path / "cache", fetcher=_fake_fetcher(),
        )

    row = conn.execute("SELECT completeness_tier FROM stores WHERE store_id = ?", (store_id,)).fetchone()
    assert row["completeness_tier"] == "known"


def test_confirm_verified_fields_promotes_to_verified(tmp_path: Path) -> None:
    conn, store_id = _censused_db(tmp_path)
    enrich_db.enrich_store_from_url(
        conn, store_id, "https://example-store.invalid/",
        cache_root=tmp_path / "cache", fetcher=_fake_fetcher(),
    )

    enrich_db.confirm_verified_fields(
        conn,
        store_id,
        address="Tokyo, Taito-ku, Ueno 1-2-3",
        hours=[{"day_of_week": "mon", "open": "18:00", "close": "24:00"}],
        pricing_model="time_based_seat_charge",
        price_items=[{"label": "seat charge", "amount_jpy": 1500, "unit": "per_30min"}],
        verification_method="official-site",
        reliability_score=4,
        source_url="https://example-store.invalid/",
    )

    row = conn.execute("SELECT completeness_tier FROM stores WHERE store_id = ?", (store_id,)).fetchone()
    assert row["completeness_tier"] == "verified"

    enrichment = conn.execute("SELECT * FROM store_enrichment WHERE store_id = ?", (store_id,)).fetchone()
    assert enrichment["verification_method"] == "official-site"
    assert enrichment["reliability_score"] == 4

    log_types = [row["change_type"] for row in conn.execute("SELECT change_type FROM store_change_log WHERE store_id = ?", (store_id,))]
    assert "initial_capture" in log_types  # from census
    assert "url_change" in log_types  # from enrich
    assert "correction" in log_types  # from confirm
