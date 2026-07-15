# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0013-lodging-famous
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
## Market Research — Kabukicho Survival Map (task-0013-lodging-famous)

Read-only research per the output contract; no repository files modified.

### Part 1: グランカスタマ歌舞伎町店 — ambiguity resolved

**Finding: グランカスタマ歌舞伎町店 is a genuinely distinct business from ブース ネットカフェ&カプセル. It is NOT a duplicate.**

The prior task-0011 exclusion was based on an unverified claim that both businesses shared the same address. Direct verification this round shows they do not:

| | グランカスタマ歌舞伎町店 | ブース ネットカフェ&カプセル |
|---|---|---|
| Address | 歌舞伎町**2**-37-1, B1F–3F | 歌舞伎町**1**-15-5 (旧ビッグレモン, 5F–8F) |
| Chome | 2-chome | 1-chome |
| Nearest station | Seibu-Shinjuku (徒歩3分, ~191m) | near Godzilla Head / Toho Bldg area |
| Source | [official site](https://g-customa.com/shop/kabuki.php), [NAVITIME](https://www.navitime.co.jp/poi?spot=01125-J003341087) | [official site](http://www.booth-netcafe.com/index.html), [yokoso-shinjuku.com](https://yokoso-shinjuku.com/lodging/capsule-hotel/booth-net-cafe-capsule/) |

These are different chome, several hundred meters apart, different buildings, different floor ranges — not a duplicate listing under two names. The existing dataset entry for Booth doesn't record an address field (only lat/lng + "ゴジラヘッド近く" description), which is consistent with 1-chome, not 2-chome — the original exclusion appears to have been an error in that prior pass, not a real conflict.

**Proposed POI (new, addition #1):**
```json
{
  "name": "グランカスタマ歌舞伎町店",
  "lat": 35.6958, "lng": 139.6994,
  "description": "歌舞伎町2-37-1、B1F〜3Fの温浴施設付きネットカフェ・漫画喫茶チェーン。西武新宿駅から徒歩3分。24時間営業、シャワー・大浴場・ランドリー完備。",
  "category": "lodging",
  "tags": ["shower_available", "overnight_friendly", "price_band_budget", "24h"],
  "reliability_score": 4,
  "source_type": "official",
  "type": "official",
  "gray_zone_note": "ネットカフェの宿泊利用は旅館業法上の宿泊施設としての許可を得たものではありません。事業自体は適法ですが、法的・安全面ではグレーゾーンに近いものとして扱ってください。",
  "licensed_as": "internet_cafe_no_lodging_license"
}
```
lat/lng is a block-level estimate from the cited address and station-distance claim (191m from Seibu-Shinjuku), not independently geocoded via a mapping API — same caveat as prior entries in this dataset.

### Part 2: broader sweep for famous/landmark lodging not yet listed

**New, distinct, in-boundary, well-known finds (2):**

| Name | Why notable | Address (cited) | Source |
|---|---|---|---|
| ホテルグレイスリー新宿 | The "Godzilla Hotel" — Godzilla head protrudes from the 8F terrace, top-floor "Godzilla Floor"; one of the most internationally recognized landmarks in Kabukicho, in the 新宿東宝ビル (Shinjuku Toho Building) | 歌舞伎町1-19-1 | [official site](https://gracery.com/shinjuku/), [access page](https://gracery.com/shinjuku/access/) |
| HOTEL GROOVE SHINJUKU, A PARKROYAL Hotel | International PARKROYAL-branded hotel occupying floors 18–38 of 東急歌舞伎町タワー (Tokyu Kabukicho Tower, opened 2023), a major recent Kabukicho landmark | 歌舞伎町1-29-1 | [official site](https://www.hotelgroove.jp/en/), [Tokyu Kabukicho Tower access](https://www.tokyu-kabukicho-tower.jp/access/) |

Confirmed distinct from existing entries: 新宿東宝ビル (1-19-1) is a different building from アパホテル新宿歌舞伎町タワー (1-20-2); Tokyu Kabukicho Tower (1-29-1) is likewise a separate building from the APA tower — verified via [APA official map](https://map.apahotel.com/map/252) vs [Tokyu Kabukicho Tower access](https://www.tokyu-kabukicho-tower.jp/access/).

**Proposed POIs (additions #2–#3):**
```json
[
  {
    "name": "ホテルグレイスリー新宿",
    "lat": 35.6953, "lng": 139.7025,
    "description": "歌舞伎町1-19-1、新宿東宝ビル内の970室・30階建てホテル。8階テラスから顔を出す実物大ゴジラヘッドが名物。JR新宿駅東口から徒歩5分、西武新宿駅から徒歩3分。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 5,
    "source_type": "official",
    "type": "official",
    "gray_zone_note": null,
    "licensed_as": "hotel_business_act"
  },
  {
    "name": "HOTEL GROOVE SHINJUKU, A PARKROYAL Hotel",
    "lat": 35.6963, "lng": 139.7033,
    "description": "歌舞伎町1-29-1、東急歌舞伎町タワー18〜38階の国際ブランドホテル(PARKROYAL)。2023年開業。西武新宿駅から徒歩1分。",
    "category": "lodging",
    "tags": ["shower_available", "overnight_friendly", "price_band_mid"],
    "reliability_score": 5,
    "source_type": "official",
    "type": "official",
    "gray_zone_note": null,
    "licensed_as": "hotel_business_act"
  }
]
```
Both lat/lng are block-level estimates relative to already-geocoded neighboring entries (APA Kabukicho Tower at 1-20-2, Toyoko Inn at 2-20-15) — not independently geocoded.

**Checked and explicitly excluded (name-recognized but disqualified):**
- **相鉄フレッサイン 東新宿駅前** — address is 新宿7-27-9, outside the Kabukicho 1/2-chome boundary (it's adjacent to, not inside, the district). Excluded per strict boundary rule. [source](https://sotetsu-hotels.com/fresa-inn/higashishinjuku/access/)
- **HOTEL KABUKI** (歌舞伎町1-16-9) — considered but not included in the proposed set. It's a real, in-boundary, boutique hotel (opened 2023, jacuzzi suites, featured in jalan/Tripadvisor rankings) but is a niche/adult-leaning boutique property rather than a broadly name-recognized landmark on the level of Gracery or Groove — flagged as a candidate for a future, less name-recognition-strict pass rather than force-fit here.

### Assumptions
- Lat/lng for all 3 new entries are block-level estimates derived from cited addresses and relative position to already-geocoded existing entries, consistent with the methodology disclosed in tasks 0008/0009/0011 — not independently geocoded via a mapping API.
- "24h" and amenity claims for グランカスタマ reflect official-site claims at time of search, not phone-verified.

### Hypotheses
- H1: The original task-0011 "same address" exclusion for グランカスタマ was likely a search-aggregation error (conflating two different Kabukicho net-cafes with similar generic descriptions) rather than a real ambiguity — worth flagging to whoever curates future exclusion notes that block-address claims should be double-checked against chome number specifically, not just re-cited.
- H2: The 東急歌舞伎町タワー (opened 2023) likely houses additional notable tenants beyond HOTEL GROOVE — worth a dedicated single-building sweep in a future task rather than assuming full coverage here.

### Recommendations
1. Add グランカスタマ歌舞伎町店 to `lodging.json` — resolves the task-0011 ambiguity definitively as "not a duplicate."
2. Add ホテルグレイスリー新宿 and HOTEL GROOVE SHINJUKU — these are the two most name-recognized/landmark lodging facilities missing from the current 21-entry dataset (Godzilla Hotel is arguably the single most internationally recognized hotel in Kabukicho).
3. Do not add 相鉄フレッサイン 東新宿駅前 (outside boundary). Consider HOTEL KABUKI only in a future non-"famous-only" pass.
4. All 3 new lat/lng values are block-level estimates — flag for geocoding-API verification before use in turn-by-turn navigation, same outstanding caveat noted in tasks 0008/0009/0011.

Sources: [g-customa.com official (Kabukicho store)](https://g-customa.com/shop/kabuki.php), [NAVITIME グランカスタマ](https://www.navitime.co.jp/poi?spot=01125-J003341087), [Booth Net Cafe & Capsule official](http://www.booth-netcafe.com/index.html), [yokoso-shinjuku.com Booth](https://yokoso-shinjuku.com/lodging/capsule-hotel/booth-net-cafe-capsule/), [Mapion 歌舞伎町2-37-1](https://www.mapion.co.jp/address/13104/30:2:37:1/), [Hotel Gracery Shinjuku official](https://gracery.com/shinjuku/), [Hotel Gracery access](https://gracery.com/shinjuku/access/), [HOTEL GROOVE SHINJUKU official](https://www.hotelgroove.jp/en/), [Tokyu Kabukicho Tower access](https://www.tokyu-kabukicho-tower.jp/access/), [APA Hotel Kabukicho Tower map](https://map.apahotel.com/map/252), [Sotetsu Fresa Inn Higashi-Shinjuku access](https://sotetsu-hotels.com/fresa-inn/higashishinjuku/access/), [HOTEL KABUKI official](https://hotel-kabuki.jp/).

