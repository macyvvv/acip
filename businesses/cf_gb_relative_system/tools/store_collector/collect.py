"""Official-source-only store data collector for cf_gb_relative_system.

Operator-run-locally tool (never wired into CI execution -- see
tools/store_collector/README.md). Fetches a SINGLE store's own official
website or SNS page directly, using a browser-like User-Agent (several
small-business sites 403 the default urllib/requests UA but accept a
normal browser one -- confirmed 2026-07-21, see
artifacts/ueno-pilot-2026-07-21/README.md). Third-party aggregator/listing
sites are never fetched: every URL is checked against
artifacts/S-011/source-register.json's deny list before any request is
made, and the store-official-website/store-official-sns categories'
next_review_at is checked too (fail-closed if that legal review has
expired, matching templates/legal-policy.yaml's own fail-closed policy).

Output is always a DRAFT record, never a promoted store-artifact.json:
extraction from arbitrary HTML is best-effort only (title, meta
description, a phone-number pattern), every other field is left for a
human/LLM reviewer to confirm. `verification_method` is deliberately never
auto-set -- a machine fetch alone does not mean a fact was verified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

TOOL_ROOT = Path(__file__).resolve().parent
BUSINESS_ROOT = TOOL_ROOT.parents[1]
SOURCE_REGISTER_PATH = BUSINESS_ROOT / "artifacts" / "S-011" / "source-register.json"

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Provisional only -- not an S-032 SLO. Cheap to compute now, safe to
# override once real per-field freshness SLOs exist.
NEXT_RECHECK_INTERVAL_DAYS = 14


class SourceDenied(Exception):
    """Raised when a URL's domain is denied, or its category review has expired."""


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int
    body: str


Fetcher = Callable[[str, str], FetchResult]


def default_fetcher(url: str, user_agent: str) -> FetchResult:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 -- operator-run tool, not app runtime
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read().decode(charset, errors="replace")
        return FetchResult(url=url, status=response.status, body=body)


def _load_source_register_entries() -> list[dict]:
    payload = json.loads(SOURCE_REGISTER_PATH.read_text(encoding="utf-8"))
    return payload["entries"]


def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def denied_domains() -> set[str]:
    """Domains explicitly marked decision=deny in source-register.json."""
    denied = set()
    for entry in _load_source_register_entries():
        owner = entry.get("owner_or_url", "")
        if entry.get("decision") == "deny" and owner.startswith("http"):
            denied.add(_domain(owner))
    return denied


def _category_expired(source_id: str, now: datetime) -> bool:
    for entry in _load_source_register_entries():
        if entry.get("source_id") == source_id:
            next_review = entry.get("next_review_at")
            if not next_review:
                return True  # no review date on record -> fail closed
            return _parse_datetime(next_review) <= now
    return True  # entry missing entirely -> fail closed


def assert_allowed(url: str, now: datetime | None = None) -> None:
    """Raise SourceDenied unless url is safe to fetch under the current
    source-register.json. Called before every fetch; never bypass this."""
    now = now or datetime.now(timezone.utc)
    domain = _domain(url)

    if domain in denied_domains():
        raise SourceDenied(
            f"{domain} is on the source-register.json deny list "
            "(third-party aggregator/listing site) -- never fetch it as a data source."
        )
    if _category_expired("store-official-website", now) and _category_expired("store-official-sns", now):
        raise SourceDenied(
            "store-official-website/store-official-sns review in "
            "artifacts/S-011/source-register.json has expired (or was never recorded) -- "
            "re-verify legal status before fetching any new source."
        )


class _TitleMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str | None = None
        self.meta_description: str | None = None
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value for key, value in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "meta" and (attrs_dict.get("name") or "").lower() == "description":
            self.meta_description = attrs_dict.get("content")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title = (self.title or "") + data


_HREF_RE = re.compile(r'href=["\'](https?://[^"\']+)["\']', re.IGNORECASE)

# (domain suffix, platform label, allow_subdomains). lit.link's own CDN
# asset host (prd.storage.lit.link) is a real subdomain that serves images,
# not a profile -- found for real against のわ's page -- so lit.link
# requires an exact netloc match, not "endswith .lit.link".
_SNS_DOMAIN_PLATFORMS = (
    ("twitter.com", "x", True),
    ("x.com", "x", True),
    ("instagram.com", "instagram", True),
    ("line.me", "line", True),
    ("lin.ee", "line", True),
    ("facebook.com", "facebook", True),
    ("tiktok.com", "tiktok", True),
    ("lit.link", "lit.link", False),
)

_MEDIA_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4", ".mov")

# Boilerplate/widget paths and hosts that are never a store's own profile:
# share buttons ("post this page to Facebook/X") and platform-internal API
# subdomains that happen to appear as <a href> targets on a platform's own
# page chrome. Found for real: Candy Side's official site has a Facebook
# share button (facebook.com/sharer/sharer.php) and an X share link
# (twitter.com/share); fetching an X profile page directly surfaces
# api.x.com in its own nav/boilerplate.
_SNS_NOISE_HOSTS = ("api.x.com", "api.twitter.com")
_SNS_NOISE_PATH_SEGMENTS = ("sharer", "share.php", "/share", "/intent/")


def _detect_sns_platform(url: str) -> str | None:
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    for domain, platform, allow_subdomains in _SNS_DOMAIN_PLATFORMS:
        if netloc == domain or (allow_subdomains and netloc.endswith("." + domain)):
            return platform
    return None


def _looks_like_valid_sns_link(url: str) -> bool:
    """Reject real-world garbage patterns found against actual Ueno pilot
    pages: a CDN media asset mis-tagged as a platform link (lit.link's
    prd.storage.lit.link/images/...); a mis-pasted double URL where a
    store entered "https:handle" as their own username on a link-in-bio
    tool (のわ's page literally contains
    href="https://www.instagram.com/https:nowa_concafe/" alongside the
    correct .../nowa_concafe/ elsewhere on the same page); and share-button/
    platform-API boilerplate that isn't a profile at all (Candy Side's
    official site links to facebook.com/sharer/sharer.php and
    twitter.com/share; X's own profile pages link to api.x.com)."""
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.lower()
    if netloc in _SNS_NOISE_HOSTS:
        return False
    if any(segment in path for segment in _SNS_NOISE_PATH_SEGMENTS):
        return False
    if path.endswith(_MEDIA_EXTENSIONS):
        return False
    if "http" in path:
        return False
    return True


def extract_sns_urls(html: str) -> list[dict]:
    """Find SNS links in <a href> attributes. Returns a deduped
    platform->url list, sorted by platform for determinism. When multiple
    candidate URLs exist for the same platform, prefers the first
    valid-looking one over a malformed one that happens to appear earlier
    in the page."""
    found: dict[str, str] = {}
    for href in _HREF_RE.findall(html):
        platform = _detect_sns_platform(href)
        if platform is None or not _looks_like_valid_sns_link(href):
            continue
        clean_url = href.split("?", 1)[0].split("#", 1)[0].rstrip("/")
        found.setdefault(platform, clean_url)
    return [{"platform": platform, "url": url} for platform, url in sorted(found.items())]


_TEL_HREF_RE = re.compile(r'href=["\']tel:([+\d\-() ]+)["\']', re.IGNORECASE)
# Negative lookaround excludes matches embedded inside a longer hyphenated
# hex run (e.g. a UUID like "...29-1086-4173-9248-315b..." otherwise
# false-positives as a phone number -- found for real against esora's and
# のわ's pages, both Strikingly/lit.link builder platforms that embed
# UUIDs in inline JSON).
_PHONE_TEXT_RE = re.compile(r"(?<![0-9a-fA-F-])0\d{1,4}-\d{1,4}-\d{3,4}(?![0-9a-fA-F-])")


@dataclass(frozen=True)
class ExtractedField:
    value: str
    confidence: str  # "extracted" | "ambiguous" | "not_found"


# Fields that free-text HTML parsing cannot reliably turn into the
# structured shapes schemas/store-artifact.json requires (hours is an
# array of day/open/close objects, price_items likewise, address needs
# human judgement to normalize). Always routed to needs_review.
ALWAYS_NEEDS_REVIEW = ("store_name", "address", "hours", "pricing_model", "price_items")


def extract_fields(html: str) -> dict[str, ExtractedField]:
    parser = _TitleMetaParser()
    parser.feed(html)
    fields: dict[str, ExtractedField] = {}

    title = (parser.title or "").strip()
    fields["page_title"] = ExtractedField(title, "extracted" if title else "not_found")

    description = (parser.meta_description or "").strip()
    fields["meta_description"] = ExtractedField(description, "extracted" if description else "not_found")

    phone_matches = _TEL_HREF_RE.findall(html) or _PHONE_TEXT_RE.findall(html)
    if len(phone_matches) == 1:
        fields["phone"] = ExtractedField(phone_matches[0].strip(), "extracted")
    elif len(phone_matches) > 1:
        fields["phone"] = ExtractedField(phone_matches[0].strip(), "ambiguous")
    else:
        fields["phone"] = ExtractedField("", "not_found")

    sns_urls = extract_sns_urls(html)
    fields["sns_urls"] = ExtractedField(
        json.dumps(sns_urls, ensure_ascii=False), "extracted" if sns_urls else "not_found"
    )

    for name in ALWAYS_NEEDS_REVIEW:
        fields[name] = ExtractedField("", "not_found")

    return fields


def _content_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _append_log(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def fetch_and_cache(
    url: str,
    store_id: str,
    cache_root: Path,
    fetcher: Fetcher = default_fetcher,
    now: datetime | None = None,
) -> dict:
    """Fetch url (after a source-register check), cache the raw body plus
    provenance, and log the attempt -- success or failure alike, so
    freshness/crawl-success metrics can be computed later without gaps."""
    now = now or datetime.now(timezone.utc)
    attempted_at = now.isoformat().replace("+00:00", "Z")
    log_path = cache_root / "fetch_log.jsonl"

    try:
        assert_allowed(url, now)
    except SourceDenied as exc:
        _append_log(log_path, {
            "url": url, "store_id": store_id, "attempted_at": attempted_at,
            "outcome": "denied", "reason": str(exc),
        })
        raise

    try:
        result = fetcher(url, DEFAULT_USER_AGENT)
    except Exception as exc:
        _append_log(log_path, {
            "url": url, "store_id": store_id, "attempted_at": attempted_at,
            "outcome": "error", "reason": str(exc),
        })
        raise

    cache_root.mkdir(parents=True, exist_ok=True)
    raw_path = cache_root / f"{store_id}.html"
    raw_path.write_text(result.body, encoding="utf-8")

    record = {
        "url": url,
        "store_id": store_id,
        "attempted_at": attempted_at,
        "http_status": result.status,
        "outcome": "success" if result.status == 200 else "http_error",
        "content_hash": _content_hash(result.body),
        "raw_path": str(raw_path),
    }
    _append_log(log_path, record)
    return record


def draft_store_artifact(store_id: str, url: str, html: str, retrieved_at: str) -> dict:
    """Build a DRAFT record. This is NEVER a valid schemas/store-artifact.json
    document by itself -- it must be reviewed and completed by a human/LLM
    before promotion into data/stores/<store_id>.json."""
    fields = extract_fields(html)
    needs_review = sorted(name for name, f in fields.items() if f.confidence != "extracted")
    next_recheck_due = (
        _parse_datetime(retrieved_at) + timedelta(days=NEXT_RECHECK_INTERVAL_DAYS)
    ).isoformat().replace("+00:00", "Z")

    draft: dict = {
        "store_id": store_id,
        "source_url": url,
        "retrieved_at": retrieved_at,
        "content_hash": _content_hash(html),
        "next_recheck_due_provisional": next_recheck_due,
        "extracted": {name: {"value": f.value, "confidence": f.confidence} for name, f in fields.items()},
        "needs_review": needs_review,
        "note": (
            "DRAFT ONLY -- not a valid schemas/store-artifact.json record. A human/LLM "
            "reviewer must confirm every field in needs_review, explicitly set "
            "verification_method (never auto-set to official-site from a machine fetch "
            "alone), and set reliability_score before this may be promoted into "
            "data/stores/<store_id>.json."
        ),
    }
    if fields["phone"].confidence == "extracted":
        draft["phone"] = fields["phone"].value
    if fields["sns_urls"].confidence == "extracted":
        draft["sns_urls"] = json.loads(fields["sns_urls"].value)
    return draft


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="cf_gb_relative_system official-source-only store collector (draft output only)."
    )
    parser.add_argument("store_id", help="Stable store_id slug, e.g. example-store-001")
    parser.add_argument("url", help="The store's own official website or SNS URL -- never an aggregator listing")
    parser.add_argument("--cache-root", type=Path, default=TOOL_ROOT / "cache")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        record = fetch_and_cache(args.url, args.store_id, args.cache_root)
    except SourceDenied as exc:
        print(f"DENIED: {exc}")
        return 2

    if record["outcome"] != "success":
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 1

    html = Path(record["raw_path"]).read_text(encoding="utf-8")
    draft = draft_store_artifact(args.store_id, args.url, html, record["attempted_at"])
    out_path = args.out or (args.cache_root / f"{args.store_id}.draft.json")
    out_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
