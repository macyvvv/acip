# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0008-lodging-deep
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
Now I have enough grounded data to compile the deep-dive lodging research.

## Market Research — Kabukicho Survival Map (task-0008-lodging-deep)

**Business:** kabukicho_survival_map | **Role:** market_research | **Task:** task-0008-lodging-deep

Read-only research per the output contract; no repository files were modified.

---

### Facts (grounded in search results, cited)

**Existing dataset gap**
- Current `lodging.json` has only 2 actual lodging entries (Booth Net Cafe & Capsule; Shinjuku Kuyakusho-mae Capsule Hotel) plus 1 non-lodging landmark (Maruhan Pachinko, explicitly not lodging).

**Capsule hotels (in/immediately bordering Kabukicho)**
- **Capsule Hotel Shinjuku 510** — 2-40-1 Kabukicho. 310 capsules; shared bath with soaking tubs, bidet toilets. [Tripadvisor](https://www.tripadvisor.com/Hotel_Review-g14133667-d1083520-Reviews-Capsule_Hotel_Shinjuku_510-Kabukicho_Shinjuku_Tokyo_Tokyo_Prefecture_Kanto.html) / [tokyo-hotels-now.com](https://www.tokyo-hotels-now.com/en/property/capsule-hotel-shinjuku-510.html)
- **Green Plaza Shinjuku Capsule Hotel** — 1-29-2 Kabukicho. One of Japan's largest: 593 men-only capsules plus a separate 30-bunk women's dormitory section, on-site sauna. [Oyster.com](https://www.oyster.com/tokyo/hotels/green-plaza-shinjuku-capsule-hotel/) / booking aggregators
- **ELE Cabin Shinjuku Kabukicho** — 2-19-3 Kabukicho. Modern capsule hotel. [hotels-tokyo-jp.com listing](https://ele-cabin-shinjuku-kabukicho.hotels-tokyo-jp.com/en/)

**Business hotels**
- **APA Hotel Shinjuku Kabukicho Tower** — 1-20-2 Kabukicho, 6 min walk from Shinjuku Station East Exit. [apahotel.com official](https://www3.apahotel.com/hotel/syutoken/tokyo/shinjuku-kabukichotower/)
- **APA Hotel Shinjuku Kabukicho Chuo** — 2-26-5 Kabukicho, 166 rooms, 7 min from Shinjuku Station East Exit. [apahotel.com official](https://www3.apahotel.com/hotel/syutoken/tokyo/shinjuku-kabukicho-chuo/)
- **Toyoko Inn Tokyo Shinjuku Kabukicho** — 2-20-15 Kabukicho, 3 min from Higashi-Shinjuku Station. [toyoko-inn.com official](https://www.toyoko-inn.com/eng/search/detail/00078/)

**Internet/manga cafes (24h, non-lodging-licensed)**
- **Kaikatsu Club Shinjuku Kabukicho-ten** — Ku Bldg 2F, 1-5-2 Kabukicho. One of the largest chains; some branches offer breakfast buffet/darts/karaoke. [Tabelog](https://tabelog.com/en/tokyo/A1304/A130401/13278782/) / [Wanderlog](https://wanderlog.com/place/details/5679184/kaikatsu-club-shinjukukabukichoten)
- **Gran Cyber Cafe Bagus Shinjuku (Kabukicho)** — Daini Toa Hall 4F, 1-21-1 Kabukicho. [Tripadvisor](https://www.tripadvisor.com/Restaurant_Review-g14133667-d8087121-Reviews-Gran_Cyber_Cafe_Bagus_Shinjuku-Kabukicho_Shinjuku_Tokyo_Tokyo_Prefecture_Kanto.html)
- **GeraGera Manga Cafe Shinjuku** — Humax Pavilion 2F, 1-20-1 Kabukicho. Note: some current listings suggest this location may be closed — flagged, not omitted, per instruction to not fabricate but also not silently drop a previously real location. [aggregator search result]

**Excluded despite being named/real** (per no-fabrication instruction, reported explicitly rather than padded in):
- **Manboo Kabukicho** (2-33-11 Kabukicho) — Tripadvisor lists this specific branch as permanently closed. Excluded from the proposed dataset; noted here only as an explicit exclusion.
- **Media Cafe Popeye Shinjuku** — address found (3-22-7 Shinjuku, Sashida Bldg B1F–2F) is in Shinjuku proper near the west exit, not inside/bordering Kabukicho, and Tabelog separately lists a same-name branch as closed. Excluded as out-of-scope/unconfirmed rather than force-fit.

**Love hotels** (real, common, legally licensed category in this specific district — included with factual, non-judgmental framing per instructions)
- Kabukicho is documented as Tokyo's densest love-hotel cluster, with dozens of properties within a 5–10 min walk of JR Shinjuku/Shinjuku-sanchome/Seibu-Shinjuku stations. [Trip101](https://trip101.com/article/love-hotels-in-kabukicho) / [Tokyo Cheapo](https://tokyocheapo.com/accommodationcat/love-hotels/)
- **Hotel Moana Shinjuku (Adults Only)** — 2-30-3 Kabukicho, 40 rooms. Note: aggregator description also claims "150m from Shin-Okubo Station," which is geographically inconsistent with a 2-30-3 Kabukicho address (Shin-Okubo is well north of Kabukicho) — flagged as a data-quality issue in the source, lowering reliability. [tokyo-hotels-now.com](https://www.tokyo-hotels-now.com/en/property/hotel-moana-shinjuku-adult-only.html)
- **HOTEL & SPA J-MEX Shinjuku Kabukicho (Adults Only)** — 2-5-6 Kabukicho. Rooms include karaoke, VOD, large-screen TV. [trivago](https://www.trivago.com/en-US/oar/hotel-spa-j-mex-shinjuku-kabukicho-adult-only-tokyo) / [booking.com](https://www.booking.com/hotel/jp/j-mex.en-gb.html)
- **HOTEL Perrier (Adults Only)** — 2-7-12 Kabukicho. Reopened Nov 2019 with 43 boutique-style rooms. [Google Maps listing](https://www.google.com/maps/place/%E3%83%9B%E3%83%86%E3%83%AB+%E3%83%9A%E3%83%AA%E3%82%A8/@35.695548,139.7038933,17z) / [Kayak](https://www.kayak.com/Tokyo-Hotels-Hotel-Perrier-Adult-Only.3654660.ksp)

**Not independently confirmed with a citable address in this pass** (mentioned by aggregators but no distinct address found): "Shinjuku Kabukicho HOTEL -AN-", "Hotel The Hotel – Shinjuku Kabukicho (Adult Only)". Excluded rather than guessed at coordinates.

**Count reached:** 11 new, distinct, individually-named, address-citable entries (3 capsule, 3 business hotel, 2 internet/manga cafe, 3 love hotel) — plus the 2 pre-existing real lodging entries gives **13 total**, short of the 15–20 target. Reported honestly per the no-fabrication instruction rather than padded with unconfirmed names.

---

### Assumptions

- Lat/lng are block-level estimates from cited chome addresses (consistent with prior deep-dive tasks' no-external-geocoding approach), not independently geocoded.
- "24h" and amenity details reflect aggregator/booking-site claims at time of search, not phone-verified.
- Love hotel entries are classified `licensed_as: love_hotel_business_act` (Japan's Business Affecting Public Morals Act / Ryokan Business Act framework covers licensed love hotels distinctly from standard hotels) — this is a standard, legal, licensed business category in Japan, not a gray-zone activity; framed factually per instructions.
- Internet/manga cafes are **not** licensed lodging (`internet_cafe_no_lodging_license`), consistent with the existing Booth Net Cafe entry's precedent.

### Hypotheses

- H1: The dataset gap to 15-20 is a real signal that Kabukicho's capsule/business-hotel supply is dominated by 2-3 chains with duplicate near-identical branches (APA, Toyoko Inn) rather than 15+ truly distinct independent operators — a follow-up pass targeting Japanese-language aggregators (not just English booking sites) would likely surface more manga-cafe and smaller capsule-hotel names that don't rank in English search.
- H2: The Manboo/Media Cafe Popeye closures suggest the manga-cafe segment in this specific district has higher turnover than capsule hotels or love hotels — worth a `last_verified` freshness flag distinct from `last_updated` for this category specifically.

---

### Proposed POI entries (draft data, additive to existing 2)

```json
[
  {
    "name": "Capsule Hotel Shinjuku 510",
    "lat": 35.6958, "lng": 139.7048,
    "description": "310-capsule hotel in Kabukicho; shared bathing area with soaking tubs and bidet toilets.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget"],
    "reliability_score": 4, "source_type": "aggregator", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "Green Plaza Shinjuku Capsule Hotel",
    "lat": 35.6945, "lng": 139.7002,
    "description": "One of Japan's largest capsule hotels: 593 men-only capsules plus a separate 30-bunk women's dormitory section, on-site sauna.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget"],
    "reliability_score": 4, "source_type": "aggregator", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "ELE Cabin Shinjuku Kabukicho",
    "lat": 35.6963, "lng": 139.7040,
    "description": "Modern capsule hotel in Kabukicho.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "APA Hotel Shinjuku Kabukicho Tower",
    "lat": 35.6950, "lng": 139.7027,
    "description": "Business hotel, 6 min walk from Shinjuku Station East Exit, in the Tokyu Kabukicho Tower area.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 5, "source_type": "official_site", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "APA Hotel Shinjuku Kabukicho Chuo",
    "lat": 35.6965, "lng": 139.7050,
    "description": "166-room business hotel, 7 min walk from Shinjuku Station East Exit.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 5, "source_type": "official_site", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "Toyoko Inn Tokyo Shinjuku Kabukicho",
    "lat": 35.6968, "lng": 139.7045,
    "description": "Business hotel chain branch, 3 min walk from Higashi-Shinjuku Station.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 5, "source_type": "official_site", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "Kaikatsu Club Shinjuku Kabukicho-ten",
    "lat": 35.6942, "lng": 139.7018,
    "description": "Internet/manga cafe chain branch; some branches offer breakfast buffet, darts, karaoke.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget", "24h"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "Internet cafe overnight stays are not licensed lodging under the Hotel Business Act -- gray-zone-adjacent for legal/safety framing even though the business is legitimate.",
    "licensed_as": "internet_cafe_no_lodging_license"
  },
  {
    "name": "Gran Cyber Cafe Bagus Shinjuku (Kabukicho)",
    "lat": 35.6941, "lng": 139.7024,
    "description": "Internet cafe chain branch in Daini Toa Hall, Kabukicho 1-chome.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget", "24h"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "Internet cafe overnight stays are not licensed lodging under the Hotel Business Act.",
    "licensed_as": "internet_cafe_no_lodging_license"
  },
  {
    "name": "GeraGera Manga Cafe Shinjuku",
    "lat": 35.6951, "lng": 139.7027,
    "description": "Manga cafe chain branch in the Humax Pavilion building; some current listings suggest possible closure, unconfirmed.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget", "24h"],
    "reliability_score": 2, "source_type": "aggregator", "type": "unofficial",
    "gray_zone_note": "Internet cafe overnight stays are not licensed lodging under the Hotel Business Act. Operating status unconfirmed as of this research pass -- verify before publishing.",
    "licensed_as": "internet_cafe_no_lodging_license"
  },
  {
    "name": "Hotel Moana Shinjuku (Adults Only)",
    "lat": 35.6970, "lng": 139.7052,
    "description": "40-room adults-only love hotel in Kabukicho 2-chome. Note: a source-cited proximity claim (150m from Shin-Okubo Station) is geographically inconsistent with the address and could not be corroborated.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 2, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "Licensed love hotel, a common and legal lodging category in this district under Japan's hotel/entertainment-business licensing framework -- not a gray-zone business, but distinct from standard hotels in room typology and guest expectations.",
    "licensed_as": "love_hotel_business_act"
  },
  {
    "name": "HOTEL & SPA J-MEX Shinjuku Kabukicho (Adults Only)",
    "lat": 35.6943, "lng": 139.7020,
    "description": "Adults-only love hotel with karaoke, VOD, and large-screen TV in rooms.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "Licensed love hotel, a common and legal lodging category in this district.",
    "licensed_as": "love_hotel_business_act"
  },
  {
    "name": "HOTEL Perrier (Adults Only)",
    "lat": 35.6955, "lng": 139.7061,
    "description": "43-room boutique-style adults-only love hotel, reopened November 2019.",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "Licensed love hotel, a common and legal lodging category in this district.",
    "licensed_as": "love_hotel_business_act"
  }
]
```

---

### Recommendations

1. Merge these **11 new entries** into `lodging.json`, bringing the real, distinct lodging count to **13** (2 existing + 11 new) — short of the 15-20 target; do not pad further without a follow-up Japanese-language search pass.
2. Run a follow-up task specifically against Japanese-language aggregators (e.g., 歌舞伎町 ネットカフェ, 歌舞伎町 カプセルホテル 一覧) to close the remaining gap to 15-20 — English-language search underrepresents smaller independent manga cafes and capsule hotels in this district.
3. Verify GeraGera Manga Cafe Shinjuku's operating status before publishing (`reliability_score: 2`); if confirmed closed, drop it rather than list a defunct business.
4. Treat all three love hotel entries as a distinct, non-judgmental, factually-framed sub-category (`licensed_as: love_hotel_business_act`) — this is standard, legal, licensed lodging in this specific district and should not be mixed with the `internet_cafe_no_lodging_license` gray-zone framing used for manga cafes.
5. Do not include "Shinjuku Kabukicho HOTEL -AN-" or "Hotel The Hotel" without a follow-up search that returns a citable address — both were repeatedly mentioned by aggregators but never with independently verifiable location data in this pass.
6. Flag Hotel Moana's Shin-Okubo proximity claim for correction or removal if it cannot be reconciled with its Kabukicho address on a second source check.

Sources: [Tripadvisor Capsule Hotel Shinjuku 510](https://www.tripadvisor.com/Hotel_Review-g14133667-d1083520-Reviews-Capsule_Hotel_Shinjuku_510-Kabukicho_Shinjuku_Tokyo_Tokyo_Prefecture_Kanto.html), [Oyster.com Green Plaza Shinjuku](https://www.oyster.com/tokyo/hotels/green-plaza-shinjuku-capsule-hotel/), [ELE Cabin listing](https://ele-cabin-shinjuku-kabukicho.hotels-tokyo-jp.com/en/), [APA Hotel Shinjuku Kabukicho Tower official](https://www3.apahotel.com/hotel/syutoken/tokyo/shinjuku-kabukichotower/), [APA Hotel Shinjuku Kabukicho Chuo official](https://www3.apahotel.com/hotel/syutoken/tokyo/shinjuku-kabukicho-chuo/), [Toyoko Inn official](https://www.toyoko-inn.com/eng/search/detail/00078/), [Tabelog Kaikatsu Club Kabukicho](https://tabelog.com/en/tokyo/A1304/A130401/13278782/), [Tripadvisor Gran Cyber Cafe Bagus](https://www.tripadvisor.com/Restaurant_Review-g14133667-d8087121-Reviews-Gran_Cyber_Cafe_Bagus_Shinjuku-Kabukicho_Shinjuku_Tokyo_Tokyo_Prefecture_Kanto.html), [Trip101 love hotels in Kabukicho](https://trip101.com/article/love-hotels-in-kabukicho), [Hotel Moana Shinjuku listing](https://www.tokyo-hotels-now.com/en/property/hotel-moana-shinjuku-adult-only.html), [J-MEX booking listing](https://www.booking.com/hotel/jp/j-mex.en-gb.html), [Hotel Perrier Google Maps](https://www.google.com/maps/place/%E3%83%9B%E3%83%86%E3%83%AB+%E3%83%9A%E3%83%AA%E3%82%A8/@35.695548,139.7038933,17z).

