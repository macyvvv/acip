from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import collect  # noqa: E402


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _fake_fetcher(body: str, status: int = 200):
    def fetcher(url: str, user_agent: str) -> collect.FetchResult:
        assert user_agent == collect.DEFAULT_USER_AGENT
        return collect.FetchResult(url=url, status=status, body=body)

    return fetcher


# -- deny-list enforcement -------------------------------------------------


def test_named_competitor_domain_is_denied() -> None:
    with pytest.raises(collect.SourceDenied):
        collect.assert_allowed("https://www.pokepara.jp/some/store")


def test_denied_url_never_reaches_the_fetcher(tmp_path: Path) -> None:
    calls = []

    def spy_fetcher(url: str, user_agent: str) -> collect.FetchResult:
        calls.append(url)
        raise AssertionError("fetcher must not be called for a denied domain")

    with pytest.raises(collect.SourceDenied):
        collect.fetch_and_cache(
            "https://moe-sta.com/shops/1",
            "should-not-fetch",
            tmp_path,
            fetcher=spy_fetcher,
        )
    assert calls == []

    log_lines = (tmp_path / "fetch_log.jsonl").read_text(encoding="utf-8").splitlines()
    logged = json.loads(log_lines[-1])
    assert logged["outcome"] == "denied"


def test_official_store_site_is_allowed() -> None:
    collect.assert_allowed("https://example-store.invalid/")


def test_expired_category_review_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stale_register = tmp_path / "source-register.json"
    stale_register.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "source_id": "store-official-website",
                        "decision": "conditional",
                        "owner_or_url": "varies per store; category-level judgment",
                        "next_review_at": "2020-01-01T00:00:00Z",
                    },
                    {
                        "source_id": "store-official-sns",
                        "decision": "conditional",
                        "owner_or_url": "varies per store; category-level judgment",
                        "next_review_at": "2020-01-01T00:00:00Z",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(collect, "SOURCE_REGISTER_PATH", stale_register)

    with pytest.raises(collect.SourceDenied):
        collect.assert_allowed("https://example-store.invalid/")


# -- extraction -------------------------------------------------------------


def test_clean_fixture_extracts_title_description_and_unambiguous_phone() -> None:
    html = (FIXTURES / "clean_store_page.html").read_text(encoding="utf-8")
    fields = collect.extract_fields(html)

    assert fields["page_title"].confidence == "extracted"
    assert "Example Store" in fields["page_title"].value
    assert fields["meta_description"].confidence == "extracted"
    assert fields["phone"].confidence == "extracted"
    assert fields["phone"].value == "03-1234-5678"


def test_phone_regex_does_not_match_uuid_fragments() -> None:
    # Regression: found for real against esora's (Strikingly) and のわ's
    # (lit.link) pages -- both embed page-builder UUIDs in inline JSON,
    # and the old loose regex mis-extracted a fragment as a confident
    # "extracted" phone number (086-4173-9248 / 054-6829-423), which would
    # have skipped needs_review entirely.
    html = '<html><body><script>{"id":"f_dfc8ff29-1086-4173-9248-315bbea1a"}</script></body></html>'
    fields = collect.extract_fields(html)

    assert fields["phone"].confidence == "not_found"


def test_fields_requiring_structured_judgement_always_need_review() -> None:
    html = (FIXTURES / "clean_store_page.html").read_text(encoding="utf-8")
    fields = collect.extract_fields(html)

    for name in collect.ALWAYS_NEEDS_REVIEW:
        assert fields[name].confidence == "not_found"


def test_missing_fields_fixture_yields_not_found_everywhere() -> None:
    html = (FIXTURES / "missing_fields_page.html").read_text(encoding="utf-8")
    fields = collect.extract_fields(html)

    assert fields["page_title"].confidence == "not_found"
    assert fields["phone"].confidence == "not_found"
    assert fields["sns_urls"].confidence == "not_found"


# -- SNS link extraction ------------------------------------------------
# Regression: found for real against 3 of the 4 Ueno pilot stores (esora,
# のわ, Voyage) -- their official pages had real X/Twitter links in
# <a href>, but extract_fields() never looked for them at all, so
# store_sns stayed empty even though the data was already fetched and
# cached. See artifacts/census-pivot-2026-07-21/ for how this was found.


def test_sns_links_are_extracted_and_deduped_by_platform() -> None:
    html = (FIXTURES / "sns_links_page.html").read_text(encoding="utf-8")
    fields = collect.extract_fields(html)

    assert fields["sns_urls"].confidence == "extracted"
    sns = json.loads(fields["sns_urls"].value)
    platforms = {entry["platform"] for entry in sns}
    assert platforms == {"x", "instagram", "line"}


def test_sns_link_query_string_and_fragment_are_stripped() -> None:
    html = (FIXTURES / "sns_links_page.html").read_text(encoding="utf-8")
    sns = collect.extract_sns_urls(html)

    x_entry = next(entry for entry in sns if entry["platform"] == "x")
    assert x_entry["url"] == "https://twitter.com/example_store"


def test_share_button_and_platform_api_boilerplate_is_rejected() -> None:
    # Regression: found for real on Candy Side's official site (a Facebook
    # share button and an X share-intent link) and on X's own profile
    # pages (which link to api.x.com in their own chrome) -- these are not
    # a store's own account and must never be captured as one.
    html = (
        '<a href="https://www.facebook.com/sharer/sharer.php?u=https://example.invalid">Share on Facebook</a>'
        '<a href="https://twitter.com/share?url=https://example.invalid">Tweet this</a>'
        '<a href="https://api.x.com/1.1/something">internal</a>'
        '<a href="https://twitter.com/real_store_handle">the real account</a>'
    )
    sns = collect.extract_sns_urls(html)

    assert [entry["platform"] for entry in sns] == ["x"]
    assert sns[0]["url"] == "https://twitter.com/real_store_handle"


def test_non_sns_links_are_not_captured() -> None:
    html = (FIXTURES / "sns_links_page.html").read_text(encoding="utf-8")
    sns = collect.extract_sns_urls(html)

    assert all("example-unrelated-blog" not in entry["url"] for entry in sns)


def test_malformed_double_url_is_rejected_in_favor_of_the_clean_one() -> None:
    # Regression: のわ's real lit.link page contains
    # href="https://www.instagram.com/https:nowa_concafe/" (a mis-pasted
    # handle) BEFORE the correct .../nowa_concafe/ elsewhere on the page.
    html = (
        '<a href="https://www.instagram.com/https:nowa_concafe/">broken, appears first</a>'
        '<a href="https://www.instagram.com/nowa_concafe/">correct, appears second</a>'
    )
    sns = collect.extract_sns_urls(html)

    instagram = next(entry for entry in sns if entry["platform"] == "instagram")
    assert instagram["url"] == "https://www.instagram.com/nowa_concafe"


def test_cdn_media_asset_on_lit_link_subdomain_is_not_captured() -> None:
    # Regression: lit.link's own asset CDN (prd.storage.lit.link) serves
    # images, not profile pages, but "endswith .lit.link" matched it.
    html = (
        '<a href="https://prd.storage.lit.link/images/creator/abc/def.png">not a profile</a>'
        '<a href="https://lit.link/en/nowa0709">the real profile</a>'
    )
    sns = collect.extract_sns_urls(html)

    assert [entry["platform"] for entry in sns] == ["lit.link"]
    assert sns[0]["url"] == "https://lit.link/en/nowa0709"


def test_clean_fixture_has_no_sns_links() -> None:
    html = (FIXTURES / "clean_store_page.html").read_text(encoding="utf-8")
    fields = collect.extract_fields(html)

    assert fields["sns_urls"].confidence == "not_found"


# -- draft assembly -----------------------------------------------------------


def test_draft_is_explicitly_marked_not_a_valid_store_artifact() -> None:
    html = (FIXTURES / "clean_store_page.html").read_text(encoding="utf-8")
    draft = collect.draft_store_artifact(
        "example-store-001", "https://example-store.invalid/", html, "2026-07-21T00:00:00Z"
    )

    assert "DRAFT ONLY" in draft["note"]
    assert "verification_method" not in draft
    assert "reliability_score" not in draft
    assert set(collect.ALWAYS_NEEDS_REVIEW) <= set(draft["needs_review"])
    assert draft["phone"] == "03-1234-5678"


def test_draft_includes_sns_urls_when_present() -> None:
    html = (FIXTURES / "sns_links_page.html").read_text(encoding="utf-8")
    draft = collect.draft_store_artifact(
        "sns-store-001", "https://example-store.invalid/", html, "2026-07-21T00:00:00Z"
    )

    assert "sns_urls" not in draft["needs_review"]
    platforms = {entry["platform"] for entry in draft["sns_urls"]}
    assert platforms == {"x", "instagram", "line"}


def test_next_recheck_due_is_provisional_interval_from_retrieval() -> None:
    html = (FIXTURES / "clean_store_page.html").read_text(encoding="utf-8")
    retrieved_at = "2026-07-21T00:00:00Z"
    draft = collect.draft_store_artifact("example-store-001", "https://example-store.invalid/", html, retrieved_at)

    expected = (
        datetime(2026, 7, 21, tzinfo=timezone.utc) + timedelta(days=collect.NEXT_RECHECK_INTERVAL_DAYS)
    ).isoformat().replace("+00:00", "Z")
    assert draft["next_recheck_due_provisional"] == expected


# -- fetch + cache (no live network -- fake fetcher only) -------------------


def test_successful_fetch_is_cached_with_provenance(tmp_path: Path) -> None:
    body = (FIXTURES / "clean_store_page.html").read_text(encoding="utf-8")
    record = collect.fetch_and_cache(
        "https://example-store.invalid/",
        "example-store-001",
        tmp_path,
        fetcher=_fake_fetcher(body),
    )

    assert record["outcome"] == "success"
    assert record["http_status"] == 200
    assert Path(record["raw_path"]).read_text(encoding="utf-8") == body
    assert record["content_hash"] == collect._content_hash(body)


def test_failed_fetch_is_logged_not_silently_dropped(tmp_path: Path) -> None:
    def failing_fetcher(url: str, user_agent: str) -> collect.FetchResult:
        raise TimeoutError("simulated network failure")

    with pytest.raises(TimeoutError):
        collect.fetch_and_cache(
            "https://example-store.invalid/",
            "example-store-001",
            tmp_path,
            fetcher=failing_fetcher,
        )

    log_lines = (tmp_path / "fetch_log.jsonl").read_text(encoding="utf-8").splitlines()
    logged = json.loads(log_lines[-1])
    assert logged["outcome"] == "error"
    assert "simulated network failure" in logged["reason"]
