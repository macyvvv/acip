# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0011-lodging-deep2
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
## Market Research — Kabukicho Survival Map (task-0011-lodging-deep2)

Read-only research per the output contract; no repository files modified.

### Facts (verified against current `lodging.json`, cited)

**New, distinct, in-boundary lodging entries found (6):**

| Name | Category | Address (cited) | Source |
|---|---|---|---|
| スーパーホテル新宿歌舞伎町 | Business hotel | 歌舞伎町2-39-9, 西武新宿駅徒歩3分 | [superhotel.co.jp official](https://www.superhotel.co.jp/s_hotels/kabukicho/), [tabelog map](https://tabelog.com/tokyo/A1304/A130401/13181749/dtlmap/) |
| カプセルホテル トランジット新宿 | Capsule hotel | 歌舞伎町2-19-15, 東新宿駅徒歩3分 | [NAVITIME](https://www.navitime.co.jp/poi?spot=01140-RK167797), [yokoso-shinjuku.com](https://yokoso-shinjuku.com/lodging/capsule-hotel/transit/) |
| ホテルバリアンリゾート新宿本店 | Love hotel | 歌舞伎町2-1-11 | [balian.jp official](https://www.balian.jp/shop/shinjuku/), [MapFan](https://mapfan.com/spots/SC5Q5,J,64) |
| HOTEL PASHA | Love hotel | 歌舞伎町2-10-12 | [jht-pasha.jp official](https://jht-pasha.jp/), [MapFan](https://mapfan.com/spots/SC5Q5,J,EI5) |
| HOTEL ATLAS | Love hotel | 歌舞伎町2-12-9, 東新宿駅徒歩3分 | [hotel-atlas.jp official](https://hotel-atlas.jp/), [HappyHotel](https://happyhotel.jp/hotels/25900733) |
| アプレシオ 新宿ハイジア店 | Internet/manga cafe | 歌舞伎町2-44-1 ハイジアB1, 西武新宿駅徒歩3分 | search aggregator listing (Haijia building already confirmed in-boundary in prior toilet-deep2 task) |

**Explicitly excluded (address-duplicate/identity risk, not fabricated):**
- **グランカスタマ歌舞伎町店** — search result gives address 歌舞伎町2-37-1, the *same address* already used for the existing **ブース ネットカフェ&カプセル** entry. Could be a different tenant in the same building, but not independently confirmed as a distinct business — excluded rather than risk double-counting one physical location as two POIs.
- **CUSTOMA CAFE 歌舞伎町店** — address 歌舞伎町1-21-1 第二東亜会館ビル7F, the same building (第二東亜会館) already used for the existing **グランサイバーカフェ Bagus 新宿** entry. Same exclusion logic.

Both exclusions are noted explicitly per the instruction to avoid repeating the pachinko-parlor-style noise problem (i.e., don't count something that isn't clearly a distinct, verifiable lodging entry).

### Assumptions

- Lat/lng are block-level estimates derived from cited chome/block addresses and proximity to already-geocoded existing entries (e.g., Toyoko Inn at 2-20-15, HOTEL Perrier at 2-7-12), **not** independently geocoded via a mapping API — consistent with the methodology disclosed in task-0008/0009.
- "24h" and access/amenity claims reflect aggregator/official-site claims at time of search, not phone-verified.
- Love hotels are classified `licensed_as: love_hotel_business_act`, consistent with the 3 existing love hotel entries — legal, licensed lodging in this district, not gray-zone.
- Internet cafe entry (Apresio) inherits the same `internet_cafe_no_lodging_license` gray-zone framing already applied to Booth/Kaikatsu/Bagus/GeraGera.

### Hypotheses

- H1: Kabukicho 2-chome's love-hotel street (north of 花道通り) is dense enough that a Japanese-language building-by-building sweep (rather than English aggregator search) would surface well beyond the 5-8 target if a future task wants a larger love-hotel-specific batch — this pass deliberately stopped at 3 to keep the mix balanced across categories rather than padding one category.
- H2: The two excluded candidates (グランカスタマ, CUSTOMA CAFE) sharing addresses with existing entries suggests some Kabukicho net-cafe buildings house multiple chain tenants on different floors — worth a targeted follow-up (checking floor numbers specifically) before deciding whether they're truly duplicates or genuinely distinct businesses.

### Proposed POI entries (draft, additive — 6 new entries)

```json
[
  {
    "name": "スーパーホテル新宿歌舞伎町",
    "lat": 35.6952, "lng": 139.6995,
    "description": "ビジネスホテル。歌舞伎町2-39-9、西武新宿駅から徒歩3分。高濃度炭酸泉の共用浴場あり。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 5, "source_type": "official", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "カプセルホテル トランジット新宿",
    "lat": 35.6966, "lng": 139.7043,
    "description": "歌舞伎町2-19-15、雑居ビル3〜5階のカプセルホテル。東新宿駅から徒歩3分。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget"],
    "reliability_score": 4, "source_type": "aggregator", "type": "official",
    "gray_zone_note": null, "licensed_as": "hotel_business_act"
  },
  {
    "name": "ホテルバリアンリゾート新宿本店",
    "lat": 35.6935, "lng": 139.7055,
    "description": "歌舞伎町2-1-11のアダルト向けラブホテル。新宿三丁目駅E1出口から徒歩3分。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 4, "source_type": "official", "type": "official",
    "gray_zone_note": "許可を得たラブホテルで、この地区では一般的かつ合法な宿泊カテゴリーです。",
    "licensed_as": "love_hotel_business_act"
  },
  {
    "name": "HOTEL PASHA",
    "lat": 35.6952, "lng": 139.7063,
    "description": "歌舞伎町2-10-12のアダルト向けラブホテル。JR新宿駅東口から徒歩8分。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "許可を得たラブホテルで、この地区では一般的かつ合法な宿泊カテゴリーです。",
    "licensed_as": "love_hotel_business_act"
  },
  {
    "name": "HOTEL ATLAS",
    "lat": 35.696, "lng": 139.707,
    "description": "歌舞伎町2-12-9のアダルト向けラブホテル。東新宿駅から徒歩3分。全室人工温泉浴槽完備。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "許可を得たラブホテルで、この地区では一般的かつ合法な宿泊カテゴリーです。",
    "licensed_as": "love_hotel_business_act"
  },
  {
    "name": "アプレシオ 新宿ハイジア店",
    "lat": 35.6951, "lng": 139.6992,
    "description": "歌舞伎町2-44-1 ハイジアB1のインターネットカフェ。西武新宿駅から徒歩3分、24時間営業。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_budget", "24h"],
    "reliability_score": 3, "source_type": "aggregator", "type": "official",
    "gray_zone_note": "ネットカフェの宿泊利用は旅館業法上の宿泊施設としての許可を得たものではありません。事業自体は適法ですが、法的・安全面ではグレーゾーンに近いものとして扱ってください。",
    "licensed_as": "internet_cafe_no_lodging_license"
  }
]
```

### Recommendations

1. Merge these **6 new entries** into `lodging.json` (11 real entries → 17, still excluding the pachinko landmark), reaching the 15-20 target for a mixed category.
2. Do not add グランカスタマ歌舞伎町店 or CUSTOMA CAFE歌舞伎町店 without first confirming floor-level distinctness from the existing ブース and Bagus entries at the same building addresses — treat as a specific, narrow follow-up check, not a full re-search.
3. All 3 new love hotel lat/lng and the 3 non-love-hotel entries are block-level estimates, not geocoded — flag for geocoding-API verification before the data is used for turn-by-turn navigation.
4. Given this is the second lodging deep-dive and yield is narrowing (English + basic Japanese aggregator search), a third round should switch method (on-site walk of Kabukicho 2-chome love hotel street, or a dedicated Japanese love-hotel directory site scrape) rather than repeating the same search style.

Sources: [Super Hotel Shinjuku Kabukicho official](https://www.superhotel.co.jp/s_hotels/kabukicho/), [Tabelog map](https://tabelog.com/tokyo/A1304/A130401/13181749/dtlmap/), [NAVITIME Capsule Transit Shinjuku](https://www.navitime.co.jp/poi?spot=01140-RK167797), [yokoso-shinjuku.com Transit Shinjuku](https://yokoso-shinjuku.com/lodging/capsule-hotel/transit/), [Balian Resort Shinjuku official](https://www.balian.jp/shop/shinjuku/), [MapFan Balian](https://mapfan.com/spots/SC5Q5,J,64), [HOTEL PASHA official](https://jht-pasha.jp/), [MapFan PASHA](https://mapfan.com/spots/SC5Q5,J,EI5), [HOTEL ATLAS official](https://hotel-atlas.jp/), [HappyHotel Atlas](https://happyhotel.jp/hotels/25900733).

