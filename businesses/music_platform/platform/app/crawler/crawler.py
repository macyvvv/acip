#!/usr/bin/env python3
"""Polite web crawler with robots.txt support and SQLite output.

This crawler is intended for allowed scraping use cases where the operator
wants to avoid analytics pollution and excessive traffic.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
import html
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib import error, parse, request, robotparser


@dataclass
class CrawlRecord:
    url: str
    status: int
    fetched_at_utc: str
    content_type: str
    title: str
    text: str
    out_links: list[str]
    fetch_seconds: float


class LinkAndTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._inside_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "title":
            self._inside_title = True
        if tag == "a":
            href = None
            for key, value in attrs:
                if key == "href":
                    href = value
                    break
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._inside_title:
            self.title_parts.append(cleaned)
        self.text_parts.append(cleaned)


def clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = text.replace("\u3000", " ")
    text = parse.unquote(text) if "%" in text else text
    text = re.sub(r"&nbsp;", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def extract_element_by_id(html: str, tag: str, element_id: str) -> str | None:
    open_pat = re.compile(
        rf"<{tag}\b[^>]*\bid=\"{re.escape(element_id)}\"[^>]*>", re.IGNORECASE
    )
    match = open_pat.search(html)
    if not match:
        return None

    token_pat = re.compile(rf"</?{tag}\b[^>]*>", re.IGNORECASE)
    depth = 1
    cursor = match.end()
    while depth > 0:
        token = token_pat.search(html, cursor)
        if not token:
            return None
        token_text = token.group(0).lower()
        if token_text.startswith(f"</{tag}"):
            depth -= 1
        else:
            depth += 1
        cursor = token.end()

    return html[match.start() : cursor]


def extract_first_element_by_class(html: str, tag: str, class_name: str) -> str | None:
    class_pat = re.compile(
        rf"<{tag}\b[^>]*class=\"[^\"]*\b{re.escape(class_name)}\b[^\"]*\"[^>]*>",
        re.IGNORECASE,
    )
    match = class_pat.search(html)
    if not match:
        return None

    token_pat = re.compile(rf"</?{tag}\b[^>]*>", re.IGNORECASE)
    depth = 1
    cursor = match.end()
    while depth > 0:
        token = token_pat.search(html, cursor)
        if not token:
            return None
        token_text = token.group(0).lower()
        if token_text.startswith(f"</{tag}"):
            depth -= 1
        else:
            depth += 1
        cursor = token.end()

    return html[match.start() : cursor]


def parse_count(html: str, label: str) -> int:
    match = re.search(rf"{re.escape(label)}[：:]\s*(\d+)曲", html)
    return int(match.group(1)) if match else 0


def extract_href_from_anchor_tag(anchor_tag: str) -> str | None:
    href_match = re.search(r'href="([^"]+)"', anchor_tag, flags=re.IGNORECASE)
    if not href_match:
        return None
    return html.unescape(href_match.group(1))


def parse_member_cell(cell_html: str) -> str | None:
    names = re.findall(
        r'<div[^>]*class="[^"]*entry-name[^"]*"[^>]*>(.*?)</div>',
        cell_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if names:
        cleaned = [clean_text(strip_tags(name)) for name in names]
        value = "/".join([name for name in cleaned if name])
        return value or None

    value = clean_text(strip_tags(cell_html)).replace("受付終了", "").strip()
    return value or None


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            status INTEGER NOT NULL,
            fetched_at_utc TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            out_links_json TEXT NOT NULL,
            fetch_seconds REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            reason TEXT NOT NULL,
            status INTEGER,
            content_type TEXT,
            message TEXT,
            fetched_at_utc TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_url TEXT NOT NULL UNIQUE,
            event_slug TEXT NOT NULL,
            fetched_at_utc TEXT NOT NULL,
            complete_count INTEGER NOT NULL,
            waiting_count INTEGER NOT NULL,
            event_info_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_url TEXT NOT NULL,
            event_slug TEXT NOT NULL,
            source_table TEXT NOT NULL,
            song_title TEXT NOT NULL,
            song_url TEXT,
            artist TEXT,
            status TEXT,
            vo TEXT,
            cho TEXT,
            gt1 TEXT,
            gt2 TEXT,
            ba TEXT,
            dr TEXT,
            key_part TEXT,
            fetched_at_utc TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS discovered_event_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_url TEXT NOT NULL UNIQUE,
            discovered_at_utc TEXT NOT NULL,
            source_list_url TEXT NOT NULL
        )
        """
    )


def extract_event_info(detail_html: str) -> dict[str, str]:
    info_block = extract_element_by_id(detail_html, "div", "event-info")
    if not info_block:
        return {}

    event_info: dict[str, str] = {}
    for li_html in re.findall(r"<li[^>]*>(.*?)</li>", info_block, flags=re.IGNORECASE | re.DOTALL):
        label_match = re.search(
            r'<span[^>]*class="[^"]*label-common[^"]*"[^>]*>(.*?)</span>',
            li_html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not label_match:
            continue
        key = clean_text(strip_tags(label_match.group(1)))
        value_html = li_html[label_match.end() :]
        value = clean_text(strip_tags(value_html))
        if key and value:
            event_info[key] = value
    return event_info


def extract_song_rows(detail_html: str, wrapper_id: str, source_table: str, event_url: str) -> list[dict[str, str | None]]:
    wrapper = extract_element_by_id(detail_html, "div", wrapper_id)
    if not wrapper:
        return []

    table_match = re.search(r"<table[^>]*>(.*?)</table>", wrapper, flags=re.IGNORECASE | re.DOTALL)
    if not table_match:
        return []

    table_html = table_match.group(1)
    tbody_match = re.search(r"<tbody[^>]*>(.*?)</tbody>", table_html, flags=re.IGNORECASE | re.DOTALL)
    if not tbody_match:
        return []

    rows: list[dict[str, str | None]] = []
    for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody_match.group(1), flags=re.IGNORECASE | re.DOTALL):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.IGNORECASE | re.DOTALL)
        if len(cells) < 10:
            continue

        song_anchor = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', cells[0], flags=re.IGNORECASE | re.DOTALL)
        song_url = parse.urljoin(event_url, song_anchor.group(1)) if song_anchor else None
        song_title = clean_text(strip_tags(song_anchor.group(2))) if song_anchor else clean_text(strip_tags(cells[0]))

        row = {
            "source_table": source_table,
            "song_title": song_title,
            "song_url": song_url,
            "artist": clean_text(strip_tags(cells[1])) or None,
            "status": clean_text(strip_tags(cells[2])) or None,
            "vo": parse_member_cell(cells[3]),
            "cho": parse_member_cell(cells[4]),
            "gt1": parse_member_cell(cells[5]),
            "gt2": parse_member_cell(cells[6]),
            "ba": parse_member_cell(cells[7]),
            "dr": parse_member_cell(cells[8]),
            "key_part": parse_member_cell(cells[9]),
        }
        rows.append(row)

    return rows


def extract_event_urls_from_list_page(
    list_html: str,
    base_url: str,
    include_old_events: bool,
) -> list[str]:
    container_ids = ["NewEvent-content"]
    if include_old_events:
        container_ids.append("OldEvent-content")

    urls: list[str] = []
    seen: set[str] = set()
    skip_roots = {
        "event",
        "database",
        "guide",
        "tag",
        "activity",
        "mypage",
        "login",
        "logout",
    }

    for container_id in container_ids:
        parent_id = container_id.replace("-content", "")
        parent_block = extract_element_by_id(list_html, "div", parent_id)
        if not parent_block:
            continue
        container = extract_element_by_id(parent_block, "ul", container_id)
        if not container:
            continue
        for href in re.findall(r'href="([^"]+)"', container, flags=re.IGNORECASE):
            absolute = normalize_url(parse.urljoin(base_url, href), drop_query=True)
            split = parse.urlsplit(absolute)
            path = split.path.strip("/")
            if not path or "/" in path:
                continue
            if path in skip_roots:
                continue
            if absolute in seen:
                continue
            seen.add(absolute)
            urls.append(absolute)

    return urls


def extract_next_list_page_urls(list_html: str, base_url: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for anchor in re.findall(r"<a[^>]*>", list_html, flags=re.IGNORECASE):
        if 'rel="next"' not in anchor.lower():
            continue
        href = extract_href_from_anchor_tag(anchor)
        if not href:
            continue
        absolute = parse.urljoin(base_url, href)
        if absolute in seen:
            continue
        seen.add(absolute)
        urls.append(absolute)
    return urls


def extract_next_list_page_url(list_html: str, base_url: str) -> str | None:
    urls = extract_next_list_page_urls(list_html, base_url)
    return urls[0] if urls else None


def build_increment_list_urls(
    start_url: str,
    max_new_event_pages: int,
    include_old_events: bool,
    max_old_event_pages: int,
) -> list[str]:
    start_split = parse.urlsplit(start_url)
    base_list_url = parse.urlunsplit((start_split.scheme, start_split.netloc, "/event/event_list", "", ""))

    urls: list[str] = []
    seen: set[str] = set()

    def append_url(url: str) -> None:
        normalized = normalize_url(url, drop_query=False)
        if normalized in seen:
            return
        seen.add(normalized)
        urls.append(normalized)

    for page in range(1, max_new_event_pages + 1):
        append_url(f"{base_list_url}?page={page}&model=NewEvent")

    if include_old_events:
        for page in range(1, max_old_event_pages + 1):
            append_url(f"{base_list_url}?page={page}&model=OldEvent")

    return urls


def crawl_bandoff(
    start_url: str,
    output_dir: Path,
    delay_seconds: float,
    timeout: float,
    user_agent: str,
    max_list_pages: int,
    max_events: int,
    include_old_events: bool,
    max_old_event_pages: int,
    list_paging_mode: str,
    respect_robots: bool,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "crawl.db"

    normalized_start = normalize_url(start_url, drop_query=False)
    robots = load_robots(normalized_start, user_agent, timeout) if respect_robots else None

    discovered_event_urls: list[str] = []
    visited_list_pages: set[str] = set()
    if list_paging_mode == "increment":
        list_queue: deque[str] = deque(
            build_increment_list_urls(
                normalized_start,
                max_new_event_pages=max_list_pages,
                include_old_events=include_old_events,
                max_old_event_pages=max_old_event_pages,
            )
        )
    else:
        list_queue = deque([normalized_start])
    list_page_budget = len(list_queue) if list_paging_mode == "increment" else max_list_pages
    list_page_count = 0
    list_page_succeeded = 0

    with sqlite3.connect(str(db_path)) as conn:
        ensure_tables(conn)
        conn.execute("DELETE FROM failures")
        conn.execute("DELETE FROM events")
        conn.execute("DELETE FROM songs")
        conn.execute("DELETE FROM discovered_event_urls")

        while list_queue and list_page_count < list_page_budget and len(discovered_event_urls) < max_events:
            list_url = list_queue.popleft()
            list_page_count += 1
            normalized_list_url = normalize_url(list_url, drop_query=False)
            if normalized_list_url in visited_list_pages:
                continue
            visited_list_pages.add(normalized_list_url)

            if robots is not None and not robots.can_fetch(user_agent, normalized_list_url):
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (normalized_list_url, "robots_disallow", None, None, None, now_utc_iso()),
                )
                break

            try:
                _, _, list_html = fetch_bandoff_list_html(
                    normalized_list_url,
                    timeout,
                    user_agent,
                    referer_url=normalized_start,
                )
            except error.HTTPError as exc:
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (normalized_list_url, "http_error", exc.code, None, str(exc), now_utc_iso()),
                )
                continue
            except Exception as exc:
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (normalized_list_url, "fetch_error", None, None, str(exc), now_utc_iso()),
                )
                continue

            list_page_succeeded += 1
            page_event_urls = extract_event_urls_from_list_page(
                list_html, normalized_list_url, include_old_events
            )
            for event_url in page_event_urls:
                if event_url in discovered_event_urls or len(discovered_event_urls) >= max_events:
                    continue
                discovered_event_urls.append(event_url)
                conn.execute(
                    """
                    INSERT OR IGNORE INTO discovered_event_urls (event_url, discovered_at_utc, source_list_url)
                    VALUES (?, ?, ?)
                    """,
                    (event_url, now_utc_iso(), normalized_list_url),
                )

            if list_paging_mode == "auto":
                for next_url in extract_next_list_page_urls(list_html, normalized_list_url):
                    normalized_next = normalize_url(next_url, drop_query=False)
                    if normalized_next in visited_list_pages:
                        continue
                    list_queue.append(normalized_next)
            time.sleep(delay_seconds)

        fetched_events = 0
        for event_url in discovered_event_urls:
            if fetched_events >= max_events:
                break

            if robots is not None and not robots.can_fetch(user_agent, event_url):
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (event_url, "robots_disallow", None, None, None, now_utc_iso()),
                )
                continue

            try:
                _, _, detail_html = fetch_html(event_url, timeout, user_agent)
                event_info = extract_event_info(detail_html)
                complete_count = parse_count(detail_html, "成立")
                waiting_count = parse_count(detail_html, "未成立")
                event_slug = parse.urlsplit(event_url).path.strip("/")

                conn.execute(
                    """
                    INSERT INTO events (
                        event_url,
                        event_slug,
                        fetched_at_utc,
                        complete_count,
                        waiting_count,
                        event_info_json
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_url,
                        event_slug,
                        now_utc_iso(),
                        complete_count,
                        waiting_count,
                        json.dumps(event_info, ensure_ascii=False),
                    ),
                )

                song_rows = extract_song_rows(detail_html, "completeTableWrap", "complete", event_url)
                song_rows.extend(
                    extract_song_rows(detail_html, "waitingTableWrap", "waiting", event_url)
                )

                for song in song_rows:
                    conn.execute(
                        """
                        INSERT INTO songs (
                            event_url,
                            event_slug,
                            source_table,
                            song_title,
                            song_url,
                            artist,
                            status,
                            vo,
                            cho,
                            gt1,
                            gt2,
                            ba,
                            dr,
                            key_part,
                            fetched_at_utc
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            event_url,
                            event_slug,
                            song["source_table"],
                            song["song_title"],
                            song["song_url"],
                            song["artist"],
                            song["status"],
                            song["vo"],
                            song["cho"],
                            song["gt1"],
                            song["gt2"],
                            song["ba"],
                            song["dr"],
                            song["key_part"],
                            now_utc_iso(),
                        ),
                    )

                fetched_events += 1
                time.sleep(delay_seconds)
            except error.HTTPError as exc:
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (event_url, "http_error", exc.code, None, str(exc), now_utc_iso()),
                )
            except Exception as exc:
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (event_url, "extract_error", None, None, str(exc), now_utc_iso()),
                )

        conn.commit()

    summary = {
        "mode": "bandoff",
        "start_url": normalized_start,
        "list_paging_mode": list_paging_mode,
        "max_new_event_pages": max_list_pages,
        "max_old_event_pages": max_old_event_pages,
        "list_pages_attempted": list_page_count,
        "list_pages_succeeded": list_page_succeeded,
        "max_list_pages": max_list_pages,
        "max_events": max_events,
        "include_old_events": include_old_events,
        "discovered_events": len(discovered_event_urls),
        "fetched_events": fetched_events,
        "generated_at_utc": now_utc_iso(),
        "output_files": {
            "database": str(db_path),
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_url(url: str, *, drop_query: bool) -> str:
    split = parse.urlsplit(url)
    scheme = split.scheme.lower()
    netloc = split.netloc.lower()
    path = split.path or "/"
    query = "" if drop_query else split.query
    normalized = parse.urlunsplit((scheme, netloc, path, query, ""))
    return normalized


def same_domain(url: str, allowed_host: str) -> bool:
    return parse.urlsplit(url).netloc.lower() == allowed_host.lower()


def text_preview(text: str, max_chars: int) -> str:
    return text[:max_chars]


def parse_links(base_url: str, links: Iterable[str], *, drop_query: bool) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for href in links:
        absolute = parse.urljoin(base_url, href)
        split = parse.urlsplit(absolute)
        if split.scheme not in {"http", "https"}:
            continue
        normalized = normalize_url(absolute, drop_query=drop_query)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def fetch_html(url: str, timeout: float, user_agent: str) -> tuple[int, str, str]:
    req = request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    with request.urlopen(req, timeout=timeout) as response:
        status = response.getcode()
        content_type = response.headers.get("Content-Type", "")
        payload = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        html = payload.decode(charset, errors="replace")
        return status, content_type, html


def fetch_bandoff_list_html(
    url: str,
    timeout: float,
    user_agent: str,
    referer_url: str,
) -> tuple[int, str, str]:
    split = parse.urlsplit(url)
    query = parse.parse_qs(split.query)
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Referer": referer_url,
    }
    if split.path == "/event/event_list" and "page" in query and "model" in query:
        headers["X-Requested-With"] = "XMLHttpRequest"

    req = request.Request(url, headers=headers, method="GET")
    with request.urlopen(req, timeout=timeout) as response:
        status = response.getcode()
        content_type = response.headers.get("Content-Type", "")
        payload = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        html = payload.decode(charset, errors="replace")
        return status, content_type, html


def load_robots(start_url: str, user_agent: str, timeout: float) -> robotparser.RobotFileParser:
    split = parse.urlsplit(start_url)
    robots_url = parse.urlunsplit((split.scheme, split.netloc, "/robots.txt", "", ""))
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)

    try:
        req = request.Request(robots_url, headers={"User-Agent": user_agent}, method="GET")
        with request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace").splitlines()
            rp.parse(body)
    except Exception:
        # Fail open to avoid false negatives when robots is temporarily unreachable.
        rp.parse([])

    return rp


def crawl(
    start_url: str,
    output_dir: Path,
    max_pages: int,
    delay_seconds: float,
    timeout: float,
    user_agent: str,
    max_text_chars: int,
    include_query: bool,
    respect_robots: bool,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_dir / "crawl.db"

    normalized_start = normalize_url(start_url, drop_query=not include_query)
    allowed_host = parse.urlsplit(normalized_start).netloc

    robots = load_robots(normalized_start, user_agent, timeout) if respect_robots else None

    queue: deque[str] = deque([normalized_start])
    seen: set[str] = set()

    crawled = 0
    with sqlite3.connect(str(db_path)) as conn:
        ensure_tables(conn)
        conn.execute("DELETE FROM pages")
        conn.execute("DELETE FROM failures")

        while queue and crawled < max_pages:
            url = queue.popleft()
            if url in seen:
                continue
            seen.add(url)

            if robots is not None and not robots.can_fetch(user_agent, url):
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (url, "robots_disallow", None, None, None, now_utc_iso()),
                )
                continue

            started = time.perf_counter()
            try:
                status, content_type, html = fetch_html(url, timeout, user_agent)
                elapsed = time.perf_counter() - started

                if "text/html" not in content_type.lower():
                    conn.execute(
                        """
                        INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (url, "non_html", status, content_type, None, now_utc_iso()),
                    )
                    time.sleep(delay_seconds)
                    continue

                parser = LinkAndTextParser()
                parser.feed(html)
                out_links = parse_links(url, parser.links, drop_query=not include_query)
                internal_links = [link for link in out_links if same_domain(link, allowed_host)]

                for next_url in internal_links:
                    if next_url not in seen:
                        queue.append(next_url)

                record = CrawlRecord(
                    url=url,
                    status=status,
                    fetched_at_utc=now_utc_iso(),
                    content_type=content_type,
                    title=" ".join(parser.title_parts).strip(),
                    text=text_preview(" ".join(parser.text_parts).strip(), max_text_chars),
                    out_links=internal_links,
                    fetch_seconds=round(elapsed, 3),
                )
                conn.execute(
                    """
                    INSERT INTO pages (
                        url,
                        status,
                        fetched_at_utc,
                        content_type,
                        title,
                        text,
                        out_links_json,
                        fetch_seconds
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.url,
                        record.status,
                        record.fetched_at_utc,
                        record.content_type,
                        record.title,
                        record.text,
                        json.dumps(record.out_links, ensure_ascii=False),
                        record.fetch_seconds,
                    ),
                )
                crawled += 1
                time.sleep(delay_seconds)
            except error.HTTPError as exc:
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (url, "http_error", exc.code, None, str(exc), now_utc_iso()),
                )
                time.sleep(delay_seconds)
            except Exception as exc:
                conn.execute(
                    """
                    INSERT INTO failures (url, reason, status, content_type, message, fetched_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (url, "fetch_error", None, None, str(exc), now_utc_iso()),
                )
                time.sleep(delay_seconds)

        conn.commit()

    summary = {
        "start_url": normalized_start,
        "allowed_host": allowed_host,
        "max_pages": max_pages,
        "crawled_pages": crawled,
        "generated_at_utc": now_utc_iso(),
        "output_files": {
            "database": str(db_path),
        },
        "notes": [
            "This crawler does not execute JavaScript, which usually avoids client-side analytics tagging.",
            "Respect target site terms and robots directives before production use.",
        ],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Polite domain-limited crawler with robots support and SQLite output."
    )
    parser.add_argument(
        "--mode",
        choices=("generic", "bandoff"),
        default="generic",
        help="Crawler mode: generic (domain BFS) or bandoff (event->songs extraction)",
    )
    parser.add_argument("start_url", help="Start URL for crawl (http/https)")
    parser.add_argument(
        "--output-dir",
        default="crawl_output",
        help="Directory to write crawl.db and summary.json",
    )
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to crawl")
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=1.5,
        help="Delay between requests in seconds",
    )
    parser.add_argument("--timeout", type=float, default=15.0, help="Request timeout in seconds")
    parser.add_argument(
        "--user-agent",
        default="acip-music-platform-crawler/0.1 (+respectful crawl)",
        help="User-Agent header",
    )
    parser.add_argument(
        "--max-text-chars",
        type=int,
        default=6000,
        help="Max extracted text chars to keep per page",
    )
    parser.add_argument(
        "--include-query",
        action="store_true",
        help="Treat query strings as distinct URLs",
    )
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Disable robots check (use only when legally permitted)",
    )
    parser.add_argument(
        "--max-list-pages",
        type=int,
        default=30,
        help="(bandoff mode) Maximum NewEvent list pages to traverse",
    )
    parser.add_argument(
        "--max-old-event-pages",
        type=int,
        default=134,
        help="(bandoff mode) Maximum OldEvent list pages to traverse when included",
    )
    parser.add_argument(
        "--list-paging-mode",
        choices=("increment", "auto"),
        default="increment",
        help="(bandoff mode) increment=page parameter increment, auto=follow rel=next",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=500,
        help="(bandoff mode) Maximum event detail pages to extract",
    )
    parser.add_argument(
        "--exclude-old-events",
        action="store_true",
        help="(bandoff mode) Exclude links from #OldEvent-content",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    start = parse.urlsplit(args.start_url)
    if start.scheme not in {"http", "https"}:
        print("error: start_url must be http or https", file=sys.stderr)
        return 2

    if args.max_pages <= 0:
        print("error: --max-pages must be positive", file=sys.stderr)
        return 2

    if args.delay_seconds < 0:
        print("error: --delay-seconds cannot be negative", file=sys.stderr)
        return 2

    if args.max_list_pages <= 0:
        print("error: --max-list-pages must be positive", file=sys.stderr)
        return 2

    if args.max_events <= 0:
        print("error: --max-events must be positive", file=sys.stderr)
        return 2

    if args.max_old_event_pages <= 0:
        print("error: --max-old-event-pages must be positive", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    if args.mode == "bandoff":
        return crawl_bandoff(
            start_url=args.start_url,
            output_dir=output_dir,
            delay_seconds=args.delay_seconds,
            timeout=args.timeout,
            user_agent=args.user_agent,
            max_list_pages=args.max_list_pages,
            max_events=args.max_events,
            include_old_events=not args.exclude_old_events,
            max_old_event_pages=args.max_old_event_pages,
            list_paging_mode=args.list_paging_mode,
            respect_robots=not args.ignore_robots,
        )

    return crawl(
        start_url=args.start_url,
        output_dir=output_dir,
        max_pages=args.max_pages,
        delay_seconds=args.delay_seconds,
        timeout=args.timeout,
        user_agent=args.user_agent,
        max_text_chars=args.max_text_chars,
        include_query=args.include_query,
        respect_robots=not args.ignore_robots,
    )


if __name__ == "__main__":
    raise SystemExit(main())
