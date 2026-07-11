# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0005-convenience-deep
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
## Market Research — Kabukicho Survival Map (task-0005-convenience-deep)

**Business:** kabukicho_survival_map | **Role:** market_research | **Task:** task-0005-convenience-deep

Read-only research per the output contract; no repository files were modified.

---

### Facts (grounded in search results, cited)

**Existing dataset gap**
- Current dataset (`task-0002/latest.json`) has exactly 2 convenience-store entries, both labeled "(Shinjuku Station-adjacent)" at lat/lng ~35.6906–35.6908, 139.7001–139.7003 — i.e. west of Kabukicho's actual chome boundaries, not inside the district.

**Chain presence confirmed inside Kabukicho 1-chome / 2-chome**
- 7-Eleven: multiple stores with 歌舞伎町 (Kabukicho) addresses confirmed via NAVITIME/Tabelog, including one branded "Kabukicho Nichome Higashi Ten" that co-hosts a Seven Bank ATM and a ChargeSPOT battery-rental unit. [navitime.co.jp](https://www.navitime.co.jp/category/0201001001/13104031000/), [tabelog.com](https://tabelog.com/en/tokyo/A1304/A130401/13234121/), [navitime.co.jp/poi 0000022792](https://www.navitime.co.jp/poi?spot=07008-0000022792)
- Lawson: at least 3 distinct Kabukicho-addressed stores, all listed as 24h. [areamarker.com/210803](https://www.areamarker.com/lawson/info/210803), [areamarker.com/260600](https://www.areamarker.com/lawson/info/260600), [e-map.ne.jp/210803](https://www.e-map.ne.jp/p/lawson/dtl/210803/), [e-map.ne.jp/260600](https://www.e-map.ne.jp/p/lawson/dtl/260600/)
- FamilyMart: at least 7 distinct Kabukicho-addressed stores per the official store-locator (store.family.co.jp / chizumaru.com), spanning both 1-chome and 2-chome, including one directly bordering Golden Gai. [store.family.co.jp/points/26489](https://store.family.co.jp/points/26489), [as.chizumaru.com bid=57912](https://as.chizumaru.com/famima/detailMap?account=famima&accmd=0&bid=57912), [as.chizumaru.com bid=26793](https://as.chizumaru.com/famima/detailMap?account=famima&accmd=0&bid=26793), [mapion.co.jp](https://www.mapion.co.jp/phonebook/M02005/13104/ILSP0059674234_ipclm/)
- Ministop: 2 distinct Kabukicho 2-chome stores, both 24h per Ministop's own store locator. [map.ministop.co.jp/detail/0000000767](https://map.ministop.co.jp/detail/0000000767/), [map.ministop.co.jp/detail/0000001065](https://map.ministop.co.jp/detail/0000001065/)
- Daily Yamazaki: searched specifically, no citable Kabukicho-addressed store found — not included.
- 7-Eleven / Seven Bank ATMs: Seven Bank ATMs are standard in-store fixtures at 7-Eleven nationwide and specifically documented at the Kabukicho Nichome Higashi store (already noted generically in task-0002's ATM entry). [pkg.navitime.co.jp/sevenbank](https://pkg.navitime.co.jp/sevenbank/spot/detail?code=0000022792)

**Naming/sourcing caveat**
- The 7-Eleven at Kabukicho 1-2-13 appears under two different display names across sources ("西武新宿駅前店" in one NAVITIME result, "新宿区役所通り店" in another) — likely the same physical store with inconsistent aggregator labeling, not two stores. Treated as one entry, flagged.
- A "Lawson Grand Cusuma Kabukicho" result (Kabukicho 2-37-1) surfaced from a single low-quality aggregator snippet with a store name that doesn't match standard Lawson naming conventions — excluded rather than reported, per the no-fabrication instruction.

**Count reached:** 18 distinct, individually-named, citable convenience-store entries (6 × 7-Eleven, 3 × Lawson, 7 × FamilyMart, 2 × Ministop) — within the requested 15–20 range.

---

### Assumptions

- Store hours labeled "24h" are as stated by chain store-locators/aggregators at time of search, not independently phone/on-site verified — consistent with the caution already logged in task-0004 (Kabukicho conbinis reportedly restrict restroom use to customers; hours claims carry similar unverified-recency risk).
- Coordinates below are approximate block-level estimates derived from chome/banchi addresses, not geocoded via a mapping API — consistent with the no-external-API-calls constraint noted in task-0002.
- "Immediately bordering Kabukicho" is interpreted to include the FamilyMart at Kabukicho 1-1-6 (Golden Gai edge), since it sits on the district's named 1-chome block despite being at its perimeter.

### Hypotheses

- H1: Because 7-Eleven, Lawson, and FamilyMart all maintain multiple 24h stores inside Kabukicho itself (vs. the dataset's current assumption that visitors must walk to Shinjuku Station), the "24h Convenience Cluster" placeholder entry undersells actual in-district density — this should become several distinct, walkable POIs rather than one vague cluster.
- H2: The 7-Eleven with the confirmed in-store Seven Bank ATM (Kabukicho Nichome Higashi) is likely the single highest-value entry for the "essentials" category, since it combines the two most requested late-night needs (cash + goods) at one citable address — worth cross-linking with the existing ATM category entry from task-0002 rather than duplicating.

---

### Proposed POI entries (draft data)

```json
[
  {
    "category": "convenience_store", "name": "7-Eleven Kabukicho 1-2-13",
    "lat": 35.6949, "lng": 139.7013,
    "description": "7-Eleven near Seibu-Shinjuku Station, within Kabukicho 1-chome. Appears under two different aggregator-listed names for the same address (\"Seibu Shinjuku Sta.-front\" / \"Kuyakusho-dori\"); treated as one store.",
    "tags": ["24h"], "reliability_score": 3,
    "source_type": "aggregator", "type": "unofficial",
    "gray_zone_note": "Store name inconsistent across sources; address is the more reliable identifier."
  },
  {
    "category": "convenience_store", "name": "7-Eleven Shinjuku Toho Building Store",
    "lat": 35.6952, "lng": 139.7028,
    "description": "7-Eleven at Kabukicho 1-19-1, beside the Shinjuku Toho Building (Godzilla Road landmark).",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "7-Eleven Shinjuku-eki Yasukuni-dori Store",
    "lat": 35.6944, "lng": 139.7010,
    "description": "7-Eleven at Kabukicho 1-17-2, on Yasukuni-dori at the Kabukicho perimeter.",
    "tags": ["24h"], "reliability_score": 3,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "7-Eleven Kabukicho 1-26-6",
    "lat": 35.6955, "lng": 139.7020,
    "description": "7-Eleven store within Kabukicho 1-chome interior.",
    "tags": ["24h"], "reliability_score": 3,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "7-Eleven Kabukicho 2-chome Chuo Ten",
    "lat": 35.6963, "lng": 139.7038,
    "description": "7-Eleven at Kabukicho 2-33-3, central 2-chome.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "7-Eleven Kabukicho Nichome Higashi Ten",
    "lat": 35.6968, "lng": 139.7052,
    "description": "7-Eleven near Higashi-Shinjuku Station, east Kabukicho 2-chome. Hosts an in-store Seven Bank ATM and a ChargeSPOT battery-rental unit.",
    "tags": ["24h", "atm_instore", "phone_charging"], "reliability_score": 4,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "Lawson Kabukicho Icchome",
    "lat": 35.6951, "lng": 139.7025,
    "description": "Lawson at Kabukicho 1-12-6.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "Lawson Kabukicho Nichome",
    "lat": 35.6964, "lng": 139.7043,
    "description": "Lawson at Kabukicho 2-17-10.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "Lawson Toei Higashi-Shinjuku Station Front",
    "lat": 35.6957, "lng": 139.7035,
    "description": "Lawson at Kabukicho 2-3-16, near the Toei Oedo Line Higashi-Shinjuku Station entrance.",
    "tags": ["24h"], "reliability_score": 3,
    "source_type": "aggregator", "type": "unofficial"
  },
  {
    "category": "convenience_store", "name": "FamilyMart Kabukicho",
    "lat": 35.6953, "lng": 139.7018,
    "description": "FamilyMart at Kabukicho 1-27-1, listed on FamilyMart's official store locator.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "convenience_store", "name": "FamilyMart Shinjuku Kabukicho Ichibangai",
    "lat": 35.6946, "lng": 139.7017,
    "description": "FamilyMart at Kabukicho 1-18-5, on the Kabukicho Ichibangai arcade.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "convenience_store", "name": "FamilyMart Kabukicho Icchome",
    "lat": 35.6949, "lng": 139.7015,
    "description": "FamilyMart at Kabukicho 1-16-1.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "convenience_store", "name": "FamilyMart Shinjuku Golden-gai",
    "lat": 35.6944, "lng": 139.7040,
    "description": "FamilyMart at Kabukicho 1-1-6, directly bordering Golden Gai on the district's eastern edge.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official",
    "gray_zone_note": "Sits at Kabukicho's border rather than its interior."
  },
  {
    "category": "convenience_store", "name": "FamilyMart Kabukicho Kita (North)",
    "lat": 35.6969, "lng": 139.7047,
    "description": "FamilyMart at Kabukicho 2-32-7, northern 2-chome.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "convenience_store", "name": "FamilyMart Shinjuku Kabukicho",
    "lat": 35.6960, "lng": 139.7033,
    "description": "FamilyMart at Kabukicho 2-25-2.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "convenience_store", "name": "FamilyMart Shinjuku Kuyakusho-dori",
    "lat": 35.6958, "lng": 139.7030,
    "description": "FamilyMart at Kabukicho 2-10-6, on Kuyakusho-dori (Ward Office Street).",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "convenience_store", "name": "Ministop Shinjuku Kabukicho",
    "lat": 35.6966, "lng": 139.7044,
    "description": "Ministop at Kabukicho 2-22-1.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "convenience_store", "name": "Ministop Kabukicho 2-chome",
    "lat": 35.6971, "lng": 139.7050,
    "description": "Ministop at Kabukicho 2-30-13, ~4 min walk from Seibu-Shinjuku Station north exit.",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  }
]
```

---

### Recommendations

1. Replace the current generic "24h Convenience Cluster" placeholder with these 18 named entries (or a curated subset), since it currently anchors two Shinjuku Station-adjacent stores that are outside Kabukicho's actual chome boundaries.
2. Prioritize the 7-Eleven Kabukicho Nichome Higashi Ten entry for cross-linking with the existing "essentials"/ATM category, since it's the only entry in this pass with a directly documented in-store Seven Bank ATM — avoid duplicating a separate generic ATM POI for the same physical location.
3. Do a single phone/on-site verification pass on the 3 entries flagged `reliability_score: 3` (the 1-2-13 name-conflict store, the Yasukuni-dori store, and the 1-26-6 store) before shipping — these came from single-aggregator sourcing without an official-site cross-check, unlike the FamilyMart and Ministop entries which are corroborated by the chains' own store locators.
4. Deliberately excluded one low-confidence "Lawson Grand Cusuma Kabukicho" result (unusual name, single weak-aggregator source) rather than padding the count — flag for a future pass if a stronger source turns up.
5. No citable Daily Yamazaki location was found inside Kabukicho; do not add one without a fresh, verifiable source.

Sources: [navitime.co.jp (7-Eleven Kabukicho list)](https://www.navitime.co.jp/category/0201001001/13104031000/), [tabelog.com (Kabukicho Nichome Higashi)](https://tabelog.com/en/tokyo/A1304/A130401/13234121/), [tabelog.com (Kabukicho Icchome, Lawson)](https://tabelog.com/en/tokyo/A1304/A130401/13209261/), [navitime.co.jp/poi 0000022792](https://www.navitime.co.jp/poi?spot=07008-0000022792), [navitime.co.jp/poi 0000029247](https://www.navitime.co.jp/poi?spot=07008-0000029247), [pkg.navitime.co.jp/sevenbank](https://pkg.navitime.co.jp/sevenbank/spot/detail?code=0000022792), [e-map.ne.jp (Lawson 210803)](https://www.e-map.ne.jp/p/lawson/dtl/210803/), [e-map.ne.jp (Lawson 260600)](https://www.e-map.ne.jp/p/lawson/dtl/260600/), [areamarker.com (Lawson 385939)](https://www.areamarker.com/lawson/info/385939), [store.family.co.jp/points/26489](https://store.family.co.jp/points/26489), [as.chizumaru.com bid=57912](https://as.chizumaru.com/famima/detailMap?account=famima&accmd=0&bid=57912), [as.chizumaru.com bid=26793](https://as.chizumaru.com/famima/detailMap?account=famima&accmd=0&bid=26793), [mapion.co.jp phonebook](https://www.mapion.co.jp/phonebook/M02005/13104/ILSP0059674234_ipclm/), [map.yahoo.co.jp FamilyMart Kabukicho](https://map.yahoo.co.jp/v3/place/A-WBb8fIF92), [map.ministop.co.jp/detail/0000000767](https://map.ministop.co.jp/detail/0000000767/), [map.ministop.co.jp/detail/0000001065](https://map.ministop.co.jp/detail/0000001065/)

