# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0003-smoking-deep
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
## Market Research — Kabukicho Survival Map (task-0003-smoking-deep)

**Business:** kabukicho_survival_map | **Role:** market_research | **Task:** task-0003-smoking-deep

Read-only research per the output contract; no repository files were modified. This is a retry of the prior attempt, which failed on a session-limit error (exit_code=1) before producing output.

---

### Facts (grounded in search results, cited)

**Regulatory context**
- Street smoking is banned throughout Kabukicho under Shinjuku Ward ordinance, with a ¥2,000 on-the-spot fine for both cigarettes and heated tobacco, actively patrol-enforced. [hostrank.jp](https://hostrank.jp/blog/kabukicho-smoking-spots)
- Tokyu Kabukicho Tower's official FAQ states the building has **no smoking room for general customer use** and directs visitors to public smoking areas instead. [tokyu-kabukicho-tower.jp/faq](https://www.tokyu-kabukicho-tower.jp/faq/)

**Outdoor designated public smoking areas** (free, 24h, no purchase required)
- Cinecity Plaza-side public smoking area, near 歌舞伎町シネシティ広場. [hostrank.jp](https://hostrank.jp/blog/kabukicho-smoking-spots) / [CLUB JT](https://www.clubjt.jp/place/spot/pref-13/city-13004/area-11409/)
- Kabukicho 1-3-7 public smoking area. [hostrank.jp](https://hostrank.jp/blog/kabukicho-smoking-spots)
- Ōgado (大ガード) roadside smoking area — sits at Nishi-Shinjuku 7-1-1, on Kabukicho's southwest border rather than strictly inside it; included as "immediately around" per task scope, flagged as borderline. [hostrank.jp](https://hostrank.jp/blog/kabukicho-smoking-spots)

**Indoor smoking-permitted venues (izakaya/bar/yakiniku, all-seats-smoking per 喫煙マップ listings)**
- Café Renoir, Shinjuku Ōgado-yoko branch (喫茶室ルノアール 新宿大ガード横店), Nishi-Shinjuku 7-1-1 — heated tobacco compatible; same border caveat as above. [hostrank.jp](https://hostrank.jp/blog/kabukicho-smoking-spots)
- Café Renoir, TOHO Cinemas-mae branch, Kabukicho 1-14-4 (Kawashin Bldg 2F) — inside Kabukicho proper. [yokoso-shinjuku.com](https://yokoso-shinjuku.com/en/usefull-info/smoking-permitted-dining-establishments-around-shinjuku/)
- Nicobar Shinjuku (ニコバー新宿店), Kabukicho 1-2-13, 17:00–5:00, all seats smoking. [smokingmap.jp](https://smokingmap.jp/p2564.html)
- Albatross G (アルバトロスG), Golden Gai 5-Bankai, Kabukicho 1-1-7, 2F, 28 seats, 19:00–5:00. [smokingmap.jp](https://smokingmap.jp/p2661.html)
- bar ガス燈 (Bar Gaslamp), Kabukicho 1-4-12, 12 seats, Mon–Sat 19:00–5:00. [smokingmap.jp](https://smokingmap.jp/p2100.html)
- 一軒め酒場 歌舞伎町店 (Ikkenme Sakaba Kabukicho), Kabukicho 1-17-1 Kurita Bldg B1, 52 seats, open 24h. [smokingmap.jp](https://smokingmap.jp/p2566.html)
- 新宿駄菓子バー (Shinjuku Dagashi Bar), Kabukicho 1-6-2 T-Wing 5F, 90 seats. [smokingmap.jp](https://smokingmap.jp/p2236.html)
- 居酒屋一休 新宿歌舞伎町店 (Izakaya Ikkyu), Kabukicho 1-18-8 Daiichi Monami Bldg 2F, 150 seats. [smokingmap.jp](https://smokingmap.jp/p2063.html)
- 焼肉にくの音 (Yakiniku Niku no Ne), Kabukicho 1-19-3, 8F, 29 seats, private rooms for 2–8. [smokingmap.jp](https://smokingmap.jp/p1969.html)
- ゴールデン街 MISO SOUP, Kabukicho 1-1-9 (Golden Gai, Hanazono Ichiban-gai), 15 seats, 19:00–5:00. [smokingmap.jp](https://smokingmap.jp/p2456.html)
- クラクラ PART II (Kurakura Part II), Kabukicho 1-1-9 (Golden Gai), 40 seats, 19:00–2:00. [smokingmap.jp](https://smokingmap.jp/p2663.html)
- 焼肉一丁目 (Yakiniku Icchome), Kabukicho 1-26-1 Fugetsu Kaikan Bldg 2F, 46 seats. [smokingmap.jp](https://smokingmap.jp/p1929.html)
- お通 新宿歌舞伎町店 (Otsu Shinjuku Kabukicho), Kabukicho 1-11 Ikuzasu Bldg 2F, 30 seats, open 24h. [smokingmap.jp](https://smokingmap.jp/p2190.html)

**Count reached:** 16 distinct, individually-named, citable entries (14 fully inside Kabukicho 1-chome addresses + 2 flagged as border-adjacent). This is within the requested 15–20 range but toward the lower end — I did not find further genuinely distinct spots beyond these without repeating the same listing pages, and stopped rather than pad the list with uncited or duplicate venues.

---

### Assumptions

- Smoking-permitted status for the izakaya/bar entries is sourced from a listing aggregator (smokingmap.jp) current as of this search; individual venues can change policy (e.g., under Japan's 2020 Health Promotion Act amendment, small existing bars/izakayas were grandfathered into "smoking allowed" status, but this can be revoked at owner discretion) — not independently re-verified on-site.
- Seat counts and hours are as published by the aggregator, not confirmed by a live call or visit.
- Golden Gai bars (Albatross G, MISO SOUP, Kurakura PART II) are geographically at Kabukicho's eastern edge, adjacent to but administratively distinct from the "shopping district" core — included because their listed address is Kabukicho 1-chome.

### Hypotheses

- H1: The Ōgado-area entries (Café Renoir Ōgado branch, Ōgado smoking area) are likely to be a *secondary fallback* rather than a primary recommendation, since they're outside Kabukicho's core walking radius — worth a distinct `distance_from_core` or similar field if these get merged into product data, rather than treating all "smoking_area" entries as equidistant.
- H2: Because izakaya/bar smoking permission in Japan is grandfathered per-venue rather than area-wide, this category is more likely to see individual venues flip to non-smoking over time than the ward-designated outdoor spots are to close — suggesting a shorter re-verification cadence for the indoor/bar entries than for official outdoor smoking areas.

---

### Proposed POI entries (draft data)

Coordinates are **approximate**, derived from Kabukicho block-number proximity (all fall within ~35.691–35.697°N, 139.699–139.705°E), not geocoded via a mapping API — consistent with the product's no-external-API-calls NFR noted in task-0002.

```json
[
  {
    "category": "smoking_area", "name": "Cinecity Plaza-side Public Smoking Area",
    "lat": 35.6949, "lng": 139.7025,
    "description": "Ward-area outdoor designated smoking spot near Kabukicho Cinecity Plaza, free, 24h.",
    "tags": ["outdoor", "rain_ok", "crowded"], "reliability_score": 3,
    "source_type": "observed", "type": "official"
  },
  {
    "category": "smoking_area", "name": "Kabukicho 1-3-7 Public Smoking Area",
    "lat": 35.6944, "lng": 139.7033,
    "description": "Outdoor designated public smoking area listed for Kabukicho 1-chome address block 3-7.",
    "tags": ["outdoor", "rain_ok"], "reliability_score": 3,
    "source_type": "observed", "type": "official"
  },
  {
    "category": "smoking_area", "name": "Ogado (Big Guard) Roadside Smoking Area",
    "lat": 35.6928, "lng": 139.6989,
    "description": "Outdoor smoking area at Nishi-Shinjuku 7-1-1, just outside Kabukicho's southwest boundary; nearest option when approaching from Shinjuku Station side.",
    "tags": ["outdoor", "rain_ok", "crowded"], "reliability_score": 3,
    "source_type": "observed", "type": "official",
    "gray_zone_note": "Border-adjacent, not strictly inside Kabukicho district boundary."
  },
  {
    "category": "smoking_area", "name": "Cafe Renoir (Ogado-yoko branch)",
    "lat": 35.6929, "lng": 139.6987,
    "description": "Paid cafe chain location with heated-tobacco-compatible smoking seating, at the Kabukicho/Nishi-Shinjuku border.",
    "tags": ["indoor", "rain_ok"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Requires a purchase; border-adjacent to Kabukicho."
  },
  {
    "category": "smoking_area", "name": "Cafe Renoir (TOHO Cinemas-mae branch)",
    "lat": 35.6949, "lng": 139.7028,
    "description": "Paid cafe inside Kabukicho (Kawashin Bldg 2F) with an indoor designated smoking section.",
    "tags": ["indoor", "rain_ok"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Requires a purchase to use the seating."
  },
  {
    "category": "smoking_area", "name": "Nicobar Shinjuku",
    "lat": 35.6939, "lng": 139.7038,
    "description": "Bar at Kabukicho 1-2-13 with all-seats smoking allowed, open 17:00-5:00.",
    "tags": ["indoor"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Bar entry required; not a standalone smoking area."
  },
  {
    "category": "smoking_area", "name": "Albatross G (Golden Gai)",
    "lat": 35.6931, "lng": 139.7043,
    "description": "Golden Gai bar at Kabukicho 1-1-7 (5-Bankai bldg, 2F), 28 seats, all-seats smoking, 19:00-5:00.",
    "tags": ["indoor", "hidden"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Bar entry/tab required; narrow Golden Gai alley access."
  },
  {
    "category": "smoking_area", "name": "bar Gaslamp",
    "lat": 35.6947, "lng": 139.7027,
    "description": "Bar at Kabukicho 1-4-12, 12 seats, smoking allowed, Mon-Sat 19:00-5:00.",
    "tags": ["indoor"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Bar entry required."
  },
  {
    "category": "smoking_area", "name": "Ikkenme Sakaba Kabukicho",
    "lat": 35.6958, "lng": 139.7010,
    "description": "24h izakaya at Kabukicho 1-17-1 (Kurita Bldg B1), 52 seats, all-seats smoking.",
    "tags": ["indoor", "crowded"], "reliability_score": 4,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Food/drink order expected."
  },
  {
    "category": "smoking_area", "name": "Shinjuku Dagashi Bar",
    "lat": 35.6952, "lng": 139.7020,
    "description": "Izakaya-bar at Kabukicho 1-6-2 (T-Wing 5F), 90 seats, all-seats smoking, retro-candy theme.",
    "tags": ["indoor", "crowded"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Order/cover charge required."
  },
  {
    "category": "smoking_area", "name": "Izakaya Ikkyu Shinjuku Kabukicho",
    "lat": 35.6960, "lng": 139.7008,
    "description": "Large izakaya at Kabukicho 1-18-8 (Daiichi Monami Bldg 2F), 150 seats, all-seats smoking.",
    "tags": ["indoor", "crowded"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Order required."
  },
  {
    "category": "smoking_area", "name": "Yakiniku Niku no Ne",
    "lat": 35.6959, "lng": 139.7012,
    "description": "Yakiniku restaurant at Kabukicho 1-19-3 (8F), 29 seats plus private rooms, all-seats smoking.",
    "tags": ["indoor"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Meal order required."
  },
  {
    "category": "smoking_area", "name": "Golden Gai MISO SOUP",
    "lat": 35.6931, "lng": 139.7043,
    "description": "Golden Gai bar at Kabukicho 1-1-9 (Hanazono Ichiban-gai), 15 seats, all-seats smoking, 19:00-5:00.",
    "tags": ["indoor", "hidden"], "reliability_score": 2,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Very small bar; cover/bar-entry etiquette applies."
  },
  {
    "category": "smoking_area", "name": "Kurakura PART II",
    "lat": 35.6931, "lng": 139.7043,
    "description": "Golden Gai bar at Kabukicho 1-1-9, 40 seats, all-seats smoking, 19:00-2:00.",
    "tags": ["indoor", "hidden"], "reliability_score": 2,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Bar entry required; late-closing relative to other listed venues."
  },
  {
    "category": "smoking_area", "name": "Yakiniku Icchome",
    "lat": 35.6963, "lng": 139.6998,
    "description": "Yakiniku restaurant at Kabukicho 1-26-1 (Fugetsu Kaikan Bldg 2F), 46 seats, all-seats smoking.",
    "tags": ["indoor"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Meal order required."
  },
  {
    "category": "smoking_area", "name": "Otsu Shinjuku Kabukicho",
    "lat": 35.6936, "lng": 139.7015,
    "description": "24h zosui/rice-soup restaurant at Kabukicho 1-11 (Ikuzasu Bldg 2F), 30 seats, all-seats smoking.",
    "tags": ["indoor", "rain_ok"], "reliability_score": 3,
    "source_type": "observed", "type": "unofficial",
    "gray_zone_note": "Order required; open 24h so useful as a late-night fallback."
  }
]
```

---

### Recommendations

1. Treat the 14 in-boundary entries as the primary smoking-area dataset and keep the 2 Ōgado-area entries visually/flag-distinguished as "just outside Kabukicho" rather than merging them silently — the existing dataset's 2 generic placeholder entries ("Smoking Area Checkpoint" etc.) give no indication of this distinction and should be replaced, not supplemented.
2. Replace the current generic `"Smoking Area Checkpoint"` placeholder entry with the 3 outdoor official spots plus a short "these are legally designated; bars/izakayas below require a paid order" note, since street smoking is fined (¥2,000) and users need a clear official-vs-commercial distinction.
3. Because all 12 bar/izakayas/restaurant entries require a purchase to use, add a `requires_purchase: true` flag (or fold into `cost_note`) distinct from the free outdoor spots — conflating "designated smoking area" with "restaurant that happens to allow smoking" risks misleading users expecting free/no-obligation access.
4. Do a single live-verification pass (phone or on-site) before shipping, since smoking permission at individually grandfathered bars/izakayas can be revoked at owner discretion post-2020 Health Promotion Act — this is the fastest-to-go-stale category in the dataset.
5. Given only 16 genuinely distinct entries were found even with a deep search (short of the 15–20 target's upper bound), do not commission further smoking-area research passes expecting to find substantially more — the category appears close to exhausted for public, citable sources; any further growth would need on-site fieldwork rather than additional web search.

Sources: [hostrank.jp Kabukicho smoking spots](https://hostrank.jp/blog/kabukicho-smoking-spots), [Tokyu Kabukicho Tower FAQ](https://www.tokyu-kabukicho-tower.jp/faq/), [CLUB JT Cinecity Plaza](https://www.clubjt.jp/place/spot/pref-13/city-13004/area-11409/), [yokoso-shinjuku.com smoking-permitted dining](https://yokoso-shinjuku.com/en/usefull-info/smoking-permitted-dining-establishments-around-shinjuku/), [smokingmap.jp Nicobar](https://smokingmap.jp/p2564.html), [smokingmap.jp Albatross G](https://smokingmap.jp/p2661.html), [smokingmap.jp bar Gaslamp](https://smokingmap.jp/p2100.html), [smokingmap.jp Ikkenme Sakaba](https://smokingmap.jp/p2566.html), [smokingmap.jp Shinjuku Dagashi Bar](https://smokingmap.jp/p2236.html), [smokingmap.jp Izakaya Ikkyu](https://smokingmap.jp/p2063.html), [smokingmap.jp Yakiniku Niku no Ne](https://smokingmap.jp/p1969.html), [smokingmap.jp Golden Gai MISO SOUP](https://smokingmap.jp/p2456.html), [smokingmap.jp Kurakura PART II](https://smokingmap.jp/p2663.html), [smokingmap.jp Yakiniku Icchome](https://smokingmap.jp/p1929.html), [smokingmap.jp Otsu Shinjuku Kabukicho](https://smokingmap.jp/p2190.html)

