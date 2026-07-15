# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0002
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
Now I have enough grounded material to compose the research output.

## Market Research — Kabukicho Survival Map (task-0002)

**Business:** kabukicho_survival_map | **Role:** market_research | **Task:** task-0002

Per the output contract, this is read-only research; no files were written. The execution adapter persists this as the artifact. This builds on task-0001 (a concurrency demo with no substantive prior POI content) and covers the 6-category detailed POI research requested per issue #33.

**Important scope note:** `requirements.md` states the product's data pipeline may load additional data "repo 内 artifact からのみ" (repo-internal artifacts only) and must make "No external API calls" at runtime. This research artifact is itself the repo-internal artifact a future implementation task would consume — the web search below is a one-time research step, not a runtime dependency, so it doesn't conflict with that NFR.

---

### Facts (grounded in search results, cited)

**1. Smoking areas**
- Shinjuku Ward bans street smoking by ordinance (no monetary fine, patrol-guidance enforcement). [senden.tokyo](https://senden.tokyo/2025/07/19/smoking-areas-in-shinjuku/)
- Shinjuku Station West Exit Rotary has a 24h designated smoking area with smoke-separation panels; PEPE building area also 24h. [mottosuitai.com](https://mottosuitai.com/en/columns/tokyo-major-stations-smoking-areas-2026/)
- Café Renoir (喫茶室ルノアール), Shinjuku TOHO Cinemas-mae branch, 1-14-4 Kabukicho (Kawashin Bldg 2F), is a paid café with an indoor smoking area. [yokoso-shinjuku.com](https://yokoso-shinjuku.com/en/usefull-info/smoking-permitted-dining-establishments-around-shinjuku/)

**2. Toilets**
- Shinjuku Yuhodo Park (Shiki no Michi), Kabukicho 1-1, has a public toilet directly inside the Kabukicho perimeter. [yokoso-shinjuku.com](https://yokoso-shinjuku.com/en/usefull-info/shinjuku-toilet-list/)
- Tokyu Kabukicho Tower (opened 2023, 53-floor complex with hotel/cinema/game centers) includes restrooms; its gender-neutral toilet design was publicly reversed after backlash. [Japan Today](https://japantoday.com/category/national/tokyu-kabukicho-tower-backtracks-on-its-gender-neutral-toilets-rejigging-them-to-appease-public-1)
- Pachinko parlors, cinemas, and convenience stores in the area commonly have toilets, though access policy (customer-only vs public) varies by venue. [Medium](https://medium.com/@satoshiashkanemura/the-ultimate-guide-to-finding-public-toilets-in-japan-when-you-really-need-one-d6242cb9fdf1)

**3. Convenience stores**
- A Lawson location "steps from Shinjuku Station" operates 24/7 with standard konbini services. [corner.inc](https://www.corner.inc/guides/tokyo/tokyo/always-open-best-konbini-convenience-stores-in-tokyo)
- 7-Eleven stores host Seven Bank ATMs, cited as especially reliable for international cards; Shinjuku Station alone has three 7-Elevens within a 2-minute walk. [Wise](https://wise.com/us/blog/atms-in-japan) / [travelcurrencyguide.com](https://travelcurrencyguide.com/guides/city/tokyo.html)

**4. ATMs**
- Seven Bank ATMs accept Visa, Mastercard, Amex, UnionPay, JCB, Maestro, Cirrus, Discover, Diners; multilingual menus (JP/EN/CN/KR); ~¥110 international transaction fee; ¥100,000 withdrawal limit per transaction (issuer-dependent). [sevenbank.co.jp](https://www.sevenbank.co.jp/intlcard/index2.html)

**5. Coin lockers**
- JR Shinjuku Station B1F, near East Gate / Central East Gate, is the nearest large locker bank when approaching from/to Kabukicho. [tripmate.news](https://tripmate.news/posts/shinjuku-luggage-storage/)
- Medium lockers (¥500–600): ~550×355×575mm, fits 20" carry-on. Large lockers (¥700–900): ~880×355×575mm, fits standard 24" checked suitcase. [livejapan.com](https://livejapan.com/en/article-a0000274/) / [tabi22.com](https://tabi22.com/coin-locker-japan-shinjuku/)
- Shinjuku Station has ~3,600 lockers total; large lockers are frequently full by 10 AM. [jrpass.com](https://www.jrpass.com/blog/utilising-station-lockers)

**6. Lodging / internet cafes**
- Booth Net Cafe & Capsule (Kabukicho, near the Godzilla head landmark): overnight capsule stay ¥3,000 (Sat ¥3,700); net-cafe seating from ¥600/2hr (¥700 weekends/holidays), includes free drinks/ice cream and Wi-Fi; shower ¥300/30min with towel (reviews note an earlier ¥200 rate, since revised upward). [soranews24.com](https://soranews24.com/2024/07/19/is-this-cheap-us20-a-night-capsule-hotel-in-tokyos-kabukicho-a-good-value-stay/) / [tripadvisor.com](https://www.tripadvisor.com/Hotel_Review-g14133667-d9570338-Reviews-Booth_Net_Cafe_Capsule-Kabukicho_Shinjuku_Tokyo_Tokyo_Prefecture_Kanto.html)
- Shinjuku Kuyakusho-mae Capsule Hotel is a named, reviewed capsule hotel located in Kabukicho. [gltjp.com](https://www.gltjp.com/en/directory/item/11203/)
- Pachinko exists in a stable, government-tolerated legal gray zone (three-entity prize-exchange structure keeps it outside gambling law), not "illegal," but distinct from licensed lodging/retail. [Japaan](https://japaan.net/subculturevibe/cacophony-chance-pachinko/)

---

### Assumptions (stated explicitly, not directly evidenced)

- "Hidden" or hard-to-find smoking spots (basements, alley nooks used informally) exist in Kabukicho as in most dense Tokyo nightlife districts, but no source confirms specific hidden/unsafe locations — publishing unverified "hidden" spots risks steering users into venues with no confirmed legal status.
- Public toilet cleanliness/wait-time ratings (`clean`, `dirty`, `long_wait`) are highly time-of-night dependent and not captured in any static source; any score assigned here would be an estimate, not a verified fact.
- Exact lat/lng for named POIs (Booth Net Cafe & Capsule, Café Renoir, Tokyu Kabukicho Tower, Shinjuku Yuhodo Park) were not independently geocoded — this task ran with WebSearch/Read/Grep/Glob only, no mapping API, consistent with the product's "no external API calls" NFR. Coordinates below are **approximate, derived from known landmark proximity** (all POIs cluster within Kabukicho's ~300m × 400m footprint, roughly 35.693–35.696°N, 139.701–139.704°E), not verified against a geocoding service.

### Hypotheses (untested, flagged as such)

- H1: Given the gender-neutral toilet reversal at Tokyu Kabukicho Tower, the `gender_separated` tag is likely to be a high-signal filter for risk-averse users in this specific product — worth prioritizing as a first-class toilet attribute rather than a minor tag.
- H2: Coin locker availability is likely the single most time-sensitive category in this dataset (large lockers reported full by 10 AM), suggesting the product should treat `coin_lockers` availability_type as inherently `time-sensitive`/`conditional` rather than `always-available`, more aggressively than other essentials categories.
- H3: Because pachinko/net-cafe/capsule lodging occupy an adjacent-to-nightlife gray zone (not illegal, but non-standard lodging), users may conflate "unofficial" with "unsafe" — the spec's disclaimer requirement should distinguish "gray-zone but legal and reviewed" (net cafes, capsule hotels) from any venue lacking public reviews entirely.

---

### Proposed POI entries (draft data, per the 6 categories/tag sets specified)

All entries below use `reliability_score` as an editorial estimate based on source count/recency, not a measured statistic — flagged accordingly.

```json
[
  {
    "category": "smoking_area",
    "name": "Shinjuku Station West Exit Smoking Area",
    "lat": 35.6905, "lng": 139.6995,
    "description": "24h designated outdoor smoking area with smoke-separation panels near the West Exit Rotary; nearest large official smoking zone to Kabukicho.",
    "tags": ["outdoor", "rain_ok", "crowded"],
    "reliability_score": 4,
    "source_type": "official",
    "type": "official"
  },
  {
    "category": "smoking_area",
    "name": "Café Renoir (Shinjuku TOHO Cinemas-mae)",
    "lat": 35.6949, "lng": 139.7028,
    "description": "Paid café inside Kabukicho (Kawashin Bldg 2F) with an indoor designated smoking section; requires a purchase to use.",
    "tags": ["indoor", "rain_ok"],
    "reliability_score": 3,
    "source_type": "observed",
    "type": "unofficial"
  },
  {
    "category": "toilet",
    "name": "Shinjuku Yuhodo Park (Shiki no Michi) Public Toilet",
    "lat": 35.6942, "lng": 139.7031,
    "description": "Ward-maintained public toilet inside Kabukicho 1-chome, part of the Yuhodo Park pedestrian strip.",
    "tags": ["free", "gender_separated"],
    "reliability_score": 3,
    "source_type": "official",
    "type": "official"
  },
  {
    "category": "toilet",
    "name": "Tokyu Kabukicho Tower Restrooms",
    "lat": 35.6950, "lng": 139.7027,
    "description": "Restrooms inside the 53-floor entertainment/hotel complex; gender-neutral design was publicly reversed to separated facilities after backlash — layout may still be in flux.",
    "tags": ["clean", "free", "gender_separated"],
    "reliability_score": 3,
    "source_type": "observed",
    "type": "official"
  },
  {
    "category": "convenience_store",
    "name": "Lawson (Shinjuku Station-adjacent)",
    "lat": 35.6906, "lng": 139.7001,
    "description": "24/7 Lawson location a short walk from Shinjuku Station toward Kabukicho.",
    "tags": ["24h"],
    "reliability_score": 4,
    "source_type": "observed",
    "type": "official"
  },
  {
    "category": "convenience_store",
    "name": "7-Eleven with Seven Bank ATM (Shinjuku Station area)",
    "lat": 35.6908, "lng": 139.7003,
    "description": "One of three 7-Eleven locations within ~2 minutes of Shinjuku Station; combines konbini + Seven Bank ATM.",
    "tags": ["24h"],
    "reliability_score": 4,
    "source_type": "observed",
    "type": "official"
  },
  {
    "category": "atm",
    "name": "Seven Bank ATM (7-Eleven, Shinjuku/Kabukicho area)",
    "lat": 35.6908, "lng": 139.7003,
    "description": "Multilingual (JP/EN/CN/KR) ATM accepting Visa, Mastercard, Amex, UnionPay, JCB and more; ~¥110 fee, ¥100,000/withdrawal cap.",
    "tags": ["24h", "international_card_ok"],
    "reliability_score": 5,
    "source_type": "official",
    "type": "official"
  },
  {
    "category": "coin_locker",
    "name": "JR Shinjuku Station B1F Coin Lockers (East/Central East Gate)",
    "lat": 35.6900, "lng": 139.7005,
    "description": "Nearest large locker bank to Kabukicho; ~3,600 lockers station-wide; large lockers frequently full by 10 AM.",
    "tags": ["medium", "large", "suitcase_ok"],
    "reliability_score": 4,
    "source_type": "official",
    "type": "official"
  },
  {
    "category": "lodging",
    "name": "Booth Net Cafe & Capsule",
    "lat": 35.6945, "lng": 139.7020,
    "description": "Internet cafe + capsule hotel near the Godzilla head landmark. Capsule stay ~¥3,000/night (¥3,700 Sat); net-cafe seating from ¥600/2hr. Shower access is a paid add-on, not included by default.",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget"],
    "reliability_score": 4,
    "source_type": "observed",
    "type": "official"
  },
  {
    "category": "lodging",
    "name": "Shinjuku Kuyakusho-mae Capsule Hotel",
    "lat": 35.6944, "lng": 139.7038,
    "description": "Named, reviewed capsule hotel in Kabukicho, adjacent to the ward office (kuyakusho).",
    "tags": ["overnight_friendly", "price_band_budget"],
    "reliability_score": 3,
    "source_type": "observed",
    "type": "official"
  },
  {
    "category": "lodging",
    "name": "Maruhan Pachinko Parlor (gray-zone reference point, not lodging)",
    "lat": 35.6947, "lng": 139.7023,
    "description": "Included only as a gray-zone landmark/orientation point, not an actual lodging option. Legally tolerated three-entity prize-exchange structure keeps pachinko outside gambling law, but it is not licensed lodging or a rest facility.",
    "tags": [],
    "reliability_score": 2,
    "source_type": "inferred",
    "type": "unofficial"
  }
]
```

**Disclaimer flag (per spec's gray-zone requirement):** the pachinko entry and any net-cafe/capsule lodging with ambiguous overnight-stay legality under Japan's Ryokan Business Act (net cafes are not licensed lodging facilities in the same category as hotels) should carry an explicit `gray_zone_note` distinguishing "legal but unlicensed-as-lodging" from "confirmed licensed accommodation."

---

### Recommendations

1. Treat this dataset as a first draft requiring one human verification pass before merging into `data/kabukicho_map_places.json` — several fields (exact coordinates, current pricing, current gender-separation status at Tokyu Kabukicho Tower) are time-sensitive and were sourced from 2024–2026 secondary articles, not a live check.
2. Add a `verification_method` field (e.g., "web-search-2026-07", "on-site-visit") to each POI going forward, since the existing dataset's `last_verified_note` is currently a static placeholder string across every entry — this research surfaced concrete dated sources that could seed that field with real values instead.
3. For the `lodging` category specifically, add a `licensed_as` attribute (e.g., `hotel_business_act` vs `internet_cafe_no_lodging_license`) — net cafes and capsule hotels have different legal footing in Japan, and conflating them under one `lodging` tag set risks misleading a user about legal/safety guarantees.
4. Do not publish specific "hidden" smoking-spot claims without on-site verification — no source confirmed any, and inventing them would violate the "ground every claim in evidence" requirement and could create legal/safety liability if wrong.
5. Prioritize implementing coin lockers before lodging in the next data-expansion pass: the time-sensitivity evidence (full by 10 AM) makes it the highest-friction first-hour decision for an arriving visitor, more so than lodging choice.

Sources: [senden.tokyo Shinjuku smoking guide](https://senden.tokyo/2025/07/19/smoking-areas-in-shinjuku/), [MottoSuitai station smoking areas](https://mottosuitai.com/en/columns/tokyo-major-stations-smoking-areas-2026/), [yokoso-shinjuku.com smoking-permitted dining](https://yokoso-shinjuku.com/en/usefull-info/smoking-permitted-dining-establishments-around-shinjuku/), [yokoso-shinjuku.com toilet list](https://yokoso-shinjuku.com/en/usefull-info/shinjuku-toilet-list/), [Japan Today Tokyu Kabukicho Tower toilets](https://japantoday.com/category/national/tokyu-kabukicho-tower-backtracks-on-its-gender-neutral-toilets-rejigging-them-to-appease-public-1), [Medium public toilets guide](https://medium.com/@satoshiashkanemura/the-ultimate-guide-to-finding-public-toilets-in-japan-when-you-really-need-one-d6242cb9fdf1), [corner.inc konbini guide](https://www.corner.inc/guides/tokyo/tokyo/always-open-best-konbini-convenience-stores-in-tokyo), [Wise ATM guide](https://wise.com/us/blog/atms-in-japan), [Seven Bank international card info](https://www.sevenbank.co.jp/intlcard/index2.html), [tripmate.news Shinjuku luggage storage](https://tripmate.news/posts/shinjuku-luggage-storage/), [livejapan.com coin locker sizes](https://livejapan.com/en/article-a0000274/), [tabi22.com Shinjuku coin lockers](https://tabi22.com/coin-locker-japan-shinjuku/), [jrpass.com station lockers](https://www.jrpass.com/blog/utilising-station-lockers), [soranews24.com Booth Net Cafe review](https://soranews24.com/2024/07/19/is-this-cheap-us20-a-night-capsule-hotel-in-tokyos-kabukicho-a-good-value-stay/), [Tripadvisor Booth Net Cafe & Capsule](https://www.tripadvisor.com/Hotel_Review-g14133667-d9570338-Reviews-Booth_Net_Cafe_Capsule-Kabukicho_Shinjuku_Tokyo_Tokyo_Prefecture_Kanto.html), [gltjp.com Shinjuku Kuyakusho-mae Capsule Hotel](https://www.gltjp.com/en/directory/item/11203/), [Japaan pachinko gray zone](https://japaan.net/subculturevibe/cacophony-chance-pachinko/)

