#!/usr/bin/env python3
"""Resolve and persist POI coordinates by name/address hints.

Usage:
  python businesses/kabukicho_survival_map/app/scripts/fix_coordinates_by_name.py --apply

Prerequisites:
  - local.config.js contains window.KABUKICHO_GMAPS_API_KEY
  - Google Cloud key allows Geocoding API
"""

import argparse
import json
import math
import re
import socket
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
LOCAL_CONFIG = ROOT / "local.config.js"
OUT_REPORT = ROOT / "coordinate_fix_report.json"

CENTER_LAT = 35.6949
CENTER_LNG = 139.7028
MAX_ACCEPTABLE_DRIFT_M = 260
MIN_MEANINGFUL_DRIFT_M = 20
NOMINATIM_DELAY_SEC = 0.35
NOMINATIM_TIMEOUT_SEC = 8
NOMINATIM_MAX_RETRIES = 2
NOMINATIM_RETRY_BACKOFF_SEC = 0.6

FILES = [
    "toilet.json",
    "smoking.json",
    "convenience.json",
    "atm.json",
    "coin_locker.json",
    "lodging.json",
]

ADDR_RE = re.compile(r"(?:東京都)?新宿区[^。\\n,、]{0,40}\\d{1,3}-\\d{1,3}(?:-\\d{1,3})?")

ATM_PREFIXES = [
    "セブン銀行ATM",
    "ゆうちょ銀行ATM",
    "みずほ銀行ATM",
    "イオン銀行ATM",
]

# High-confidence manual anchors. These are applied first and protected from
# subsequent geocoding drift so repeated script runs cannot regress them.
MANUAL_COORD_OVERRIDES = {
    ("toilet.json", "東急歌舞伎町タワー トイレ"): (35.695935, 139.700657),
    ("toilet.json", "西武新宿駅前公衆便所"): (35.694749, 139.70014),
    ("toilet.json", "大久保公園トイレ"): (35.697439, 139.701333),
    ("toilet.json", "新宿区役所本庁舎1階トイレ"): (35.69386, 139.703447),
    ("toilet.json", "東急歌舞伎町タワー 2階トイレ"): (35.695935, 139.700657),
    ("toilet.json", "TOHOシネマズ新宿 3階トイレ"): (35.695154, 139.701964),
    ("smoking.json", "シネシティ広場前 公衆喫煙所"): (35.695154, 139.701964),
    ("smoking.json", "西武新宿駅前公衆喫煙所"): (35.694749, 139.70014),
    ("smoking.json", "新宿区立大久保公園 喫煙所"): (35.697439, 139.701333),
    ("coin_locker.json", "東急歌舞伎町タワー地下1階コインロッカー"): (35.695935, 139.700657),
    ("coin_locker.json", "東急歌舞伎町タワー4階シネマフロアロッカー"): (35.695935, 139.700657),
    ("coin_locker.json", "東急歌舞伎町タワー10階(109シネマズプレミアム新宿)ロッカー"): (35.695935, 139.700657),
    ("lodging.json", "新宿区役所前カプセルホテル"): (35.69386, 139.703447),
    ("lodging.json", "アパホテル新宿歌舞伎町タワー"): (35.695935, 139.700657),
    ("convenience.json", "セブン-イレブン歌舞伎町1-2-13店"): (35.694372, 139.703326),
    ("atm.json", "セブン銀行ATM(セブン-イレブン、新宿・歌舞伎町エリア)"): (35.689607, 139.700571),
    ("atm.json", "新宿歌舞伎町郵便局 ATM"): (35.697966, 139.702286),
}


def normalize_name_variants(name: str) -> List[str]:
    base = (name or "").strip()
    if not base:
        return []

    variants = [base]

    # Parenthetical source names often contain the real place name.
    m = re.search(r"[（(]([^()（）]{2,})[)）]", base)
    if m:
        inner = m.group(1).strip()
        if inner:
            variants.append(inner)

    # Drop noisy suffixes often used as notes in this dataset.
    cleaned = re.sub(r"[（(][^()（）]+[)）]", "", base).strip()
    cleaned = re.sub(r"・?\d+号機", "", cleaned).strip()
    if cleaned:
        variants.append(cleaned)

    # ATM wrappers frequently include the true facility name in parentheses.
    for prefix in ATM_PREFIXES:
        if cleaned.startswith(prefix):
            alt = cleaned.replace(prefix, "").strip(" ・-")
            if alt:
                variants.append(alt)

    # Common cosmetic markers that reduce hit rate.
    variants.extend([
        base.replace("新宿区役所前", "区役所前").strip(),
        base.replace("歌舞伎町", "新宿").strip(),
        base.replace("(アダルト専用)", "").replace("（アダルト専用）", "").strip(),
    ])

    deduped = []
    for v in variants:
        v = re.sub(r"\s+", " ", v).strip()
        if v and v not in deduped:
            deduped.append(v)
    return deduped[:6]


def load_key() -> str:
    env_key = __import__("os").environ.get("KABUKICHO_GMAPS_API_KEY")
    if env_key:
        return env_key

    text = LOCAL_CONFIG.read_text(encoding="utf-8")
    m = re.search(r'KABUKICHO_GMAPS_API_KEY\s*=\s*["\']([^"\']+)["\']', text)
    if not m:
        raise RuntimeError("API key not found in local.config.js")
    return m.group(1)


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000.0
    p = math.pi / 180.0
    dlat = (lat2 - lat1) * p
    dlng = (lng2 - lng1) * p
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlng / 2) ** 2
    return r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def extract_hints(entry: dict) -> List[str]:
    body = f"{entry.get('name', '')} {entry.get('description', '')} {entry.get('gray_zone_note', '')}"
    hints = []
    for m in ADDR_RE.finditer(body):
        hint = m.group(0).strip()
        if hint and hint not in hints:
            hints.append(hint)
    return hints


def build_queries(entry: dict) -> List[str]:
    name = (entry.get("name") or "").strip()
    name_variants = normalize_name_variants(name)
    if not name_variants:
        name_variants = [name]

    queries = []
    for hint in extract_hints(entry):
        queries.append(f"{name_variants[0]} {hint}".strip())
        if len(name_variants) > 1:
            queries.append(f"{name_variants[1]} {hint}".strip())
        queries.append(hint)

    for nv in name_variants:
        queries.append(f"{nv} 東京都新宿区歌舞伎町".strip())
        queries.append(f"{nv} 新宿".strip())
    queries.append(f"{name_variants[0]} Kabukicho".strip())

    deduped = []
    for q in queries:
        if q and q not in deduped:
            deduped.append(q)
    return deduped[:10]


def geocode_google(api_key: str, query: str) -> dict:
    params = {
        "address": query,
        "key": api_key,
        "region": "JP",
        "language": "ja",
        "bounds": f"{CENTER_LAT - 0.025},{CENTER_LNG - 0.025}|{CENTER_LAT + 0.025},{CENTER_LNG + 0.025}",
    }
    url = "https://maps.googleapis.com/maps/api/geocode/json?" + urlencode(params)
    with urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def geocode_nominatim(query: str) -> List[dict]:
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 5,
        "accept-language": "ja",
    }
    url = "https://nominatim.openstreetmap.org/search?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "acip-kabukicho-map-fixer/1.0"})
    last_error = None
    for attempt in range(NOMINATIM_MAX_RETRIES):
        try:
            with urlopen(req, timeout=NOMINATIM_TIMEOUT_SEC) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, socket.timeout, TimeoutError) as exc:
            last_error = exc
            if attempt >= NOMINATIM_MAX_RETRIES - 1:
                break
            time.sleep(NOMINATIM_RETRY_BACKOFF_SEC * (attempt + 1))
    if last_error:
        raise last_error
    return []


def manual_override_for(file_name: str, name: str) -> Optional[Tuple[float, float]]:
    return MANUAL_COORD_OVERRIDES.get((file_name, name))


def validate_geocoding_permission(api_key: str) -> None:
    probe = geocode_google(api_key, "東京都新宿区歌舞伎町1-1")
    status = probe.get("status")
    if status == "REQUEST_DENIED":
        msg = probe.get("error_message") or "Geocoding API permission denied"
        raise RuntimeError(
            "Geocoding API is not available for this key. "
            "Enable Geocoding API and include it in API restrictions. "
            f"Google response: {msg}"
        )


def score_nominatim_result(result: dict, old_lat: float, old_lng: float) -> Optional[dict]:
    if "lat" not in result or "lon" not in result:
        return None

    new_lat = float(result["lat"])
    new_lng = float(result["lon"])
    drift = haversine_m(old_lat, old_lng, new_lat, new_lng)
    if drift > MAX_ACCEPTABLE_DRIFT_M:
        return None

    address = result.get("display_name") or ""
    in_shinjuku = ("新宿" in address) or ("shinjuku" in address.lower())
    in_tokyo = ("東京" in address) or ("tokyo" in address.lower())
    if not in_shinjuku and not in_tokyo:
        return None

    importance = float(result.get("importance") or 0.0)
    score = (1000 - drift) + (120 if in_shinjuku else 30) + int(importance * 80)

    return {
        "new_lat": round(new_lat, 6),
        "new_lng": round(new_lng, 6),
        "drift_m": round(drift),
        "location_type": "NOMINATIM",
        "address": address,
        "score": round(score, 2),
    }


def score_result(result: dict, old_lat: float, old_lng: float) -> Optional[dict]:
    geom = result.get("geometry") or {}
    loc = geom.get("location") or {}
    if "lat" not in loc or "lng" not in loc:
        return None

    new_lat = float(loc["lat"])
    new_lng = float(loc["lng"])
    drift = haversine_m(old_lat, old_lng, new_lat, new_lng)
    if drift > MAX_ACCEPTABLE_DRIFT_M:
        return None

    address = (result.get("formatted_address") or "") + " " + " ".join(
        (c.get("long_name") or "") for c in (result.get("address_components") or [])
    )
    in_shinjuku = ("新宿" in address) or ("shinjuku" in address.lower())

    lt = geom.get("location_type") or ""
    location_score = {"ROOFTOP": 120, "RANGE_INTERPOLATED": 80, "GEOMETRIC_CENTER": 40}.get(lt, 10)
    score = (1000 - drift) + location_score + (90 if in_shinjuku else 0) - (120 if result.get("partial_match") else 0)

    return {
        "new_lat": round(new_lat, 6),
        "new_lng": round(new_lng, 6),
        "drift_m": round(drift),
        "location_type": lt,
        "address": result.get("formatted_address", ""),
        "score": round(score, 2),
    }


def should_candidate(entry: dict, coord_count: Dict[Tuple[float, float], int]) -> bool:
    def decimals(v: float) -> int:
        s = str(v)
        return len(s.split(".")[-1]) if "." in s else 0

    low_precision = min(decimals(entry.get("lat")), decimals(entry.get("lng"))) <= 3
    duplicate = coord_count[(entry.get("lat"), entry.get("lng"))] > 1
    return low_precision or duplicate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write accepted updates into JSON files")
    parser.add_argument(
        "--provider",
        choices=["auto", "google", "nominatim"],
        default="auto",
        help="Geocoding provider strategy",
    )
    parser.add_argument(
        "--manual-only",
        action="store_true",
        help="Apply only built-in manual overrides and skip network geocoding",
    )
    args = parser.parse_args()

    api_key = ""
    provider_mode = args.provider
    if not args.manual_only and provider_mode in ("auto", "google"):
        try:
            api_key = load_key()
            validate_geocoding_permission(api_key)
            provider_mode = "google"
        except Exception as exc:
            if args.provider == "google":
                raise
            provider_mode = "nominatim"
            print(f"google_geocode_unavailable: {exc}")
            print("fallback_provider: nominatim")

    rows = []
    for name in FILES:
        path = DATA_DIR / name
        arr = json.loads(path.read_text(encoding="utf-8"))
        for idx, entry in enumerate(arr):
            row = dict(entry)
            row["_file"] = name
            row["_idx"] = idx
            rows.append(row)

    coord_count = {}
    for row in rows:
        key = (row.get("lat"), row.get("lng"))
        coord_count[key] = coord_count.get(key, 0) + 1

    updates = []
    manual_updates = []
    failures = []

    for row in rows:
        manual = manual_override_for(row["_file"], row.get("name") or "")
        old_lat = float(row["lat"])
        old_lng = float(row["lng"])

        if manual:
            drift = haversine_m(old_lat, old_lng, manual[0], manual[1])
            if drift >= 1:
                item = {
                    "file": row["_file"],
                    "idx": row["_idx"],
                    "name": row.get("name"),
                    "old_lat": old_lat,
                    "old_lng": old_lng,
                    "new_lat": round(manual[0], 6),
                    "new_lng": round(manual[1], 6),
                    "drift_m": round(drift),
                    "location_type": "MANUAL_OVERRIDE",
                    "query": "manual_override",
                    "address": "curated_anchor",
                }
                updates.append(item)
                manual_updates.append(item)
            continue

        if args.manual_only:
            continue

        if not should_candidate(row, coord_count):
            continue

        best = None
        best_query = ""

        for query in build_queries(row):
            try:
                if provider_mode == "google":
                    response = geocode_google(api_key, query)
                else:
                    response = geocode_nominatim(query)
            except Exception:
                continue

            if provider_mode == "google":
                if response.get("status") != "OK":
                    continue
                for result in (response.get("results") or [])[:4]:
                    scored = score_result(result, old_lat, old_lng)
                    if not scored:
                        continue
                    if not best or scored["score"] > best["score"]:
                        best = scored
                        best_query = query
                time.sleep(0.05)
            else:
                for result in response[:5]:
                    scored = score_nominatim_result(result, old_lat, old_lng)
                    if not scored:
                        continue
                    if not best or scored["score"] > best["score"]:
                        best = scored
                        best_query = query
                time.sleep(NOMINATIM_DELAY_SEC)

        if not best:
            failures.append({"file": row["_file"], "idx": row["_idx"], "name": row.get("name")})
            continue

        if best["drift_m"] < MIN_MEANINGFUL_DRIFT_M:
            continue

        updates.append(
            {
                "file": row["_file"],
                "idx": row["_idx"],
                "name": row.get("name"),
                "old_lat": old_lat,
                "old_lng": old_lng,
                "new_lat": best["new_lat"],
                "new_lng": best["new_lng"],
                "drift_m": best["drift_m"],
                "location_type": best["location_type"],
                "query": best_query,
                "address": best["address"],
            }
        )

    report = {
        "provider": provider_mode,
        "manual_only": bool(args.manual_only),
        "total_entries": len(rows),
        "candidate_entries": sum(1 for r in rows if should_candidate(r, coord_count)),
        "accepted_updates": len(updates),
        "manual_override_updates": len(manual_updates),
        "failed_candidates": len(failures),
        "updates": sorted(updates, key=lambda x: -x["drift_m"]),
        "failures": failures,
    }
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"report: {OUT_REPORT}")
    print(f"accepted_updates: {len(updates)}")
    print(f"failed_candidates: {len(failures)}")

    if args.apply and updates:
        grouped = {}
        for update in updates:
            grouped.setdefault(update["file"], []).append(update)

        for file_name, file_updates in grouped.items():
            path = DATA_DIR / file_name
            arr = json.loads(path.read_text(encoding="utf-8"))
            for upd in file_updates:
                idx = upd["idx"]
                arr[idx]["lat"] = upd["new_lat"]
                arr[idx]["lng"] = upd["new_lng"]
            path.write_text(json.dumps(arr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        print("applied_updates: yes")
    else:
        print("applied_updates: no")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
