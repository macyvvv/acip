from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Static-site "build": no bundler, no backend -- per issue #33's constraints
# (no over-engineering). The business-owned DB lives under this app dir; the
# platform runtime JSON is the cross-platform distribution surface. This build
# exports runtime JSON first, then copies it plus the static HTML/JS/CSS into:
#   - this product dir's own data/ (so index.html can be opened/served locally)
#   - platform/web/public/kabukicho_survival_map/ (the deployable static bundle)

PRODUCT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PRODUCT_DIR.parents[2]
PLATFORM_ROOT = REPO_ROOT / "platform"
DATA_SOURCE = PLATFORM_ROOT / "system" / "runtime" / "data" / "kabukicho"
PUBLIC_DIR = PLATFORM_ROOT / "web" / "public" / "kabukicho_survival_map"
SHARED_DIR = PLATFORM_ROOT / "app" / "shared"

if str(PLATFORM_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_ROOT))

from system.core.dotenv import load_dotenv  # noqa: E402

# index.html is handled separately from the other static files -- it's a
# template with SSG:* markers that get substituted with generated content
# (see _render_index_html), not a plain copy.
STATIC_FILES = ("app.js", "style.css", "privacy.html", "terms.html", "favicon.svg")
INDEX_TEMPLATE = PRODUCT_DIR / "index.html"
# Cross-product utilities (platform/app/shared/) copied in flat alongside this
# product's own static files -- same "committed local copy of a canonical
# source" pattern as data/*.json above, since this repo has no bundler to
# resolve a relative import across product/shared directory boundaries.
SHARED_FILES = ("dom_escape.js",)
LOCAL_CONFIG_FILE = PRODUCT_DIR / "local.config.js"
PUBLIC_LOCAL_CONFIG_FILE = PUBLIC_DIR / "local.config.js"

# Mirrors app.js's CATEGORIES array (id, label, JSON filename). Kept as a
# separate literal here rather than parsed out of app.js -- no shared
# source of truth between the two currently. If a category is added/renamed
# in app.js, update this list too or the static (SSG) render will silently
# omit/mislabel it.
CATEGORIES = [
    {"id": "convenience", "file": "convenience.json", "label": "コンビニ"},
    {"id": "smoking", "file": "smoking.json", "label": "喫煙所"},
    {"id": "toilet", "file": "toilet.json", "label": "トイレ"},
    {"id": "atm", "file": "atm.json", "label": "ATM・両替"},
    {"id": "coin_locker", "file": "coin_locker.json", "label": "コインロッカー"},
    {"id": "lodging", "file": "lodging.json", "label": "宿泊・ネカフェ"},
    {"id": "karaoke", "file": "karaoke.json", "label": "カラオケ"},
    {"id": "shisha_bar", "file": "shisha_bar.json", "label": "シーシャバー"},
]

# Fixed, hand-curated FAQ content -- genuine, answerable-in-one-line
# questions a visitor (or an AI answer engine on their behalf) would
# actually ask, not SEO-keyword-stuffing filler. Rendered as visible page
# content (not hidden schema-only markup, which risks Google's structured
# data spam policy) plus FAQPage JSON-LD. See somia's sibling research: Q&A
# formatting remains one of the easiest patterns for LLMs to extract even
# though Google retired the visual FAQ rich-result snippet in 2026-05.
FAQ_ITEMS = [
    (
        "歌舞伎町に無料の喫煙所はありますか？",
        "はい。本サイトのデータは「無料で使える屋外の指定喫煙所」のみを喫煙所カテゴリに掲載しています(店舗内の喫煙可能スペースは含みません)。カテゴリ「喫煙所」からタップ1つで一覧を確認できます。",
    ),
    (
        "歌舞伎町のトイレは無料で使えますか？",
        "掲載しているトイレの多くは無料の公共トイレですが、施設ごとに条件が異なる場合があります。各POIカードのタグ(free/clean/gender_separatedなど)で個別に確認してください。",
    ),
    (
        "深夜でも使えるコインロッカーはありますか？",
        "「24h」タグが付いているコインロッカー・コンビニ・ATMは24時間利用可能です。カテゴリ内でタグ絞り込みを使うと深夜対応の施設だけに絞れます。",
    ),
    (
        "掲載されている情報はどのくらい新しいですか？",
        "各POIには最終確認日(last_updated)と信頼度スコアがあり、8日から1ヶ月以内に確認された情報には更新目安バッジ、1ヶ月以上確認されていない情報には注意バッジが付きます。",
    ),
    (
        "非公式(グレーゾーン)の情報とは何ですか？",
        "風俗営業関連施設など、公式な出典で裏付けが取りにくい場所には「⚠ 非公式情報」の注意書きを表示しています。利用は自己責任でお願いします。",
    ),
]


def _escape(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _load_category_data() -> list[tuple[dict, list[dict]]]:
    loaded = []
    for category in CATEGORIES:
        path = DATA_SOURCE / category["file"]
        pois = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        loaded.append((category, pois))
    return loaded


def _render_poi_static_html(category_data: list[tuple[dict, list[dict]]]) -> str:
    # All six categories, all POIs -- unlike app.js's runtime render (one
    # active category at a time), a crawler only gets one page load, so
    # everything needs to be present in the initial HTML at once.
    sections = []
    for category, pois in category_data:
        if not pois:
            continue
        cards = []
        for poi in pois:
            tags_html = "".join(
                '<span class="tag-chip">' + _escape(tag) + "</span>" for tag in poi.get("tags") or []
            )
            gray_zone_html = ""
            if poi.get("type") == "unofficial":
                gray_zone_html = (
                    '<div class="gray-zone-banner">⚠ 非公式情報・内容は変更される場合があります・'
                    "ご利用は自己責任でお願いします<br>"
                    "⚠ Unofficial Information / Subject to change / Use at your own risk</div>"
                )
            elif poi.get("gray_zone_note"):
                gray_zone_html = '<div class="info-note">' + _escape(poi["gray_zone_note"]) + "</div>"
            maps_url = (
                "https://www.google.com/maps/search/?api=1&query="
                + _escape(str(poi.get("lat")) + "," + str(poi.get("lng")))
            )
            cards.append(
                '<article class="poi-card">'
                "<h3>" + _escape(poi.get("name")) + "</h3>"
                + gray_zone_html
                + '<p class="description">' + _escape(poi.get("description")) + "</p>"
                '<div class="tag-row">' + tags_html + "</div>"
                '<a class="maps-link" target="_blank" rel="noopener" href="' + maps_url + '">位置情報を見る</a>'
                "</article>"
            )
        sections.append("<section><h2>" + _escape(category["label"]) + "</h2>" + "".join(cards) + "</section>")
    return "".join(sections)


def _render_faq_html() -> str:
    items = []
    for question, answer in FAQ_ITEMS:
        items.append(
            "<details><summary>" + _escape(question) + "</summary><p>" + _escape(answer) + "</p></details>"
        )
    return "<h2>よくある質問</h2>" + "".join(items)


def _render_jsonld(category_data: list[tuple[dict, list[dict]]], site_url: str) -> str:
    # Place (not LocalBusiness) for every POI -- LocalBusiness's schema
    # assumes business-identity semantics (openingHours, priceRange) that
    # don't fit a public toilet or a designated outdoor smoking spot.
    # additionalType carries the category label as a lightweight, always-
    # valid way to distinguish facility kinds without forcing a mismatched
    # LocalBusiness subtype.
    list_items = []
    position = 1
    for category, pois in category_data:
        for poi in pois:
            list_items.append(
                {
                    "@type": "ListItem",
                    "position": position,
                    "item": {
                        "@type": "Place",
                        "name": poi.get("name"),
                        "description": poi.get("description"),
                        "additionalType": category["label"],
                        "geo": {
                            "@type": "GeoCoordinates",
                            "latitude": poi.get("lat"),
                            "longitude": poi.get("lng"),
                        },
                    },
                }
            )
            position += 1

    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "歌舞伎町サバイバルマップ POI一覧",
        "itemListElement": list_items,
    }
    if site_url:
        item_list["url"] = site_url

    faq_page = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in FAQ_ITEMS
        ],
    }

    graph = json.dumps([item_list, faq_page], ensure_ascii=False, indent=2)
    return '<script type="application/ld+json">\n' + graph + "\n</script>"


def _render_index_html(category_data: list[tuple[dict, list[dict]]], site_url: str) -> str:
    template = INDEX_TEMPLATE.read_text(encoding="utf-8")
    template = template.replace("<!-- SSG:JSONLD -->", _render_jsonld(category_data, site_url))
    template = template.replace(
        '<p class="empty-state">カテゴリを選択して、歌舞伎町の施設を探してください。</p>',
        _render_poi_static_html(category_data),
    )
    template = template.replace("<!-- SSG:FAQ_CONTENT -->", _render_faq_html())
    if site_url:
        extra_tags = (
            '<link rel="canonical" href="' + _escape(site_url) + '">\n'
            '<meta property="og:url" content="' + _escape(site_url) + '">'
        )
        template = template.replace("</head>", extra_tags + "\n</head>", 1)
    return template


def _inject_public_runtime_config(html_text: str, ga_id: str, adsense_client: str) -> str:
    public_config = (
        "<script>\n"
        f"  window.KABUKICHO_GA_ID = {json.dumps(ga_id)};\n"
        f"  window.KABUKICHO_ADSENSE_CLIENT = {json.dumps(adsense_client)};\n"
        "</script>\n"
    )
    marker = '<script>\n  /* GA placeholder -- ID injected via config, never hardcoded. Empty string\n'
    if marker not in html_text:
        raise RuntimeError("Unable to inject public GA/AdSense config: template marker not found")
    return html_text.replace(marker, public_config + marker, 1)


def _write_robots_txt(site_url: str) -> None:
    # Domain-independent (relative paths only), so this is always written,
    # regardless of whether KABUKICHO_SITE_URL is set. Explicitly allows
    # standard search crawlers plus the AI answer-engine bots that respect
    # robots.txt (GPTBot/OAI-SearchBot, PerplexityBot, Google-Extended,
    # ClaudeBot, CCBot) -- several hosts/CDNs block AI bots by default, so
    # an explicit Allow is safer than relying on an absent Disallow.
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "User-agent: GPTBot",
        "Allow: /",
        "User-agent: OAI-SearchBot",
        "Allow: /",
        "User-agent: ClaudeBot",
        "Allow: /",
        "User-agent: PerplexityBot",
        "Allow: /",
        "User-agent: Google-Extended",
        "Allow: /",
        "User-agent: CCBot",
        "Allow: /",
    ]
    if site_url:
        lines += ["", f"Sitemap: {site_url.rstrip('/')}/sitemap.xml"]
    (PUBLIC_DIR / "robots.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_sitemap_xml(site_url: str) -> None:
    # Sitemap <loc> must be an absolute URL, which needs a real domain --
    # skip entirely (rather than emit a placeholder that would confuse
    # crawlers) until KABUKICHO_SITE_URL is set once a host is chosen.
    if not site_url:
        print("KABUKICHO_SITE_URL not set -- skipping sitemap.xml (needs a real absolute URL). "
              "Set it in .env once a deploy domain is chosen, then re-run build.py.")
        return
    from datetime import date

    loc = site_url.rstrip("/") + "/"
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{html.escape(loc)}</loc>\n"
        f"    <lastmod>{date.today().isoformat()}</lastmod>\n"
        "  </url>\n"
        "</urlset>\n"
    )
    (PUBLIC_DIR / "sitemap.xml").write_text(xml, encoding="utf-8")


def build() -> None:
    if not DATA_SOURCE.exists():
        raise FileNotFoundError(f"Data source not found: {DATA_SOURCE}")

    load_dotenv(REPO_ROOT / ".env")
    site_url = os.environ.get("KABUKICHO_SITE_URL", "").strip()
    ga_id = os.environ.get("KABUKICHO_GA_ID", "").strip()
    adsense_client = os.environ.get("KABUKICHO_ADSENSE_CLIENT", "").strip()

    # DB-first flow: export canonical runtime JSON from SQLite before copying
    # any data into product/public bundles. Skippable for hosting platforms
    # whose build image ships a Python without the stdlib sqlite3 module
    # (observed on Cloudflare's asdf-installed Python 3.13) -- the JSON under
    # DATA_SOURCE is already the DB's export as of the last commit, so a
    # deploy-time build can safely use it as-is without re-exporting.
    if os.environ.get("KABUKICHO_SKIP_DB_EXPORT", "").strip().lower() not in ("1", "true", "yes"):
        subprocess.run(
            [sys.executable, str(PRODUCT_DIR / "scripts" / "poi_db_sync.py"), "export-json"],
            check=True,
        )

    local_data_dir = PRODUCT_DIR / "data"
    public_data_dir = PUBLIC_DIR / "data"
    local_data_dir.mkdir(parents=True, exist_ok=True)
    public_data_dir.mkdir(parents=True, exist_ok=True)

    for data_file in DATA_SOURCE.glob("*.json"):
        shutil.copy2(data_file, local_data_dir / data_file.name)
        shutil.copy2(data_file, public_data_dir / data_file.name)

    for static_file in STATIC_FILES:
        shutil.copy2(PRODUCT_DIR / static_file, PUBLIC_DIR / static_file)

    for shared_file in SHARED_FILES:
        shutil.copy2(SHARED_DIR / shared_file, PRODUCT_DIR / shared_file)
        shutil.copy2(SHARED_DIR / shared_file, PUBLIC_DIR / shared_file)

    category_data = _load_category_data()
    rendered_index_html = _render_index_html(category_data, site_url)
    rendered_index_html = _inject_public_runtime_config(rendered_index_html, ga_id, adsense_client)
    (PUBLIC_DIR / "index.html").write_text(rendered_index_html, encoding="utf-8")
    _write_robots_txt(site_url)
    _write_sitemap_xml(site_url)

    print(f"Copied {len(list(DATA_SOURCE.glob('*.json')))} data file(s) to {local_data_dir} and {public_data_dir}")
    print(f"Copied {len(STATIC_FILES)} static file(s) + rendered index.html to {PUBLIC_DIR}")
    print(f"Copied {len(SHARED_FILES)} shared file(s) from {SHARED_DIR} to {PRODUCT_DIR} and {PUBLIC_DIR}")
    print(f"GA4 enabled in public bundle: {'yes' if ga_id else 'no'}")
    print(f"AdSense enabled in public bundle: {'yes' if adsense_client else 'no'}")

    _write_local_gmaps_config()


def _write_local_gmaps_config() -> None:
    # Local-dev-only convenience: if the operator has set a real Google
    # Maps JS API key in .env, write it into a small, gitignored file that
    # index.html loads (as a script tag, before the window.KABUKICHO_
    # GMAPS_API_KEY placeholder) purely so the map renders during local
    # testing. Deliberately NOT written into PUBLIC_DIR -- that bundle is
    # tracked in git, and this key must never be committed there. A real
    # production deploy needs its own separate key-injection step, tied to
    # whichever host is eventually chosen (not yet decided).
    # load_dotenv() populates os.environ as a side effect (without
    # overriding a variable already set in the real shell environment) --
    # read back from there, matching this repo's established convention
    # (see platform/system/scripts/platform/somia/providers_kling.py) rather than relying on
    # its returned dict, which only reflects the file, not a real
    # shell-exported KABUKICHO_GMAPS_API_KEY.
    load_dotenv(REPO_ROOT / ".env")
    api_key = os.environ.get("KABUKICHO_GMAPS_API_KEY", "")
    config_paths = [LOCAL_CONFIG_FILE, PUBLIC_LOCAL_CONFIG_FILE]
    if not api_key:
        for path in config_paths:
            if path.exists():
                path.unlink()
        return
    config_text = (
        "// Generated by build.py from .env's KABUKICHO_GMAPS_API_KEY.\n"
        "// Build artifact -- do not edit by hand; edit .env or the host's\n"
        "// deployment environment instead. Google Maps API keys are browser-side\n"
        "// keys and must be referrer-restricted in Google Cloud Console.\n"
        f"window.KABUKICHO_GMAPS_API_KEY = {json.dumps(api_key)};\n"
    )
    for path in config_paths:
        path.write_text(config_text, encoding="utf-8")
    print(
        f"Wrote Google Maps API key config to {LOCAL_CONFIG_FILE} and {PUBLIC_LOCAL_CONFIG_FILE} "
        "(local dev + deploy artifact)"
    )


if __name__ == "__main__":
    build()
