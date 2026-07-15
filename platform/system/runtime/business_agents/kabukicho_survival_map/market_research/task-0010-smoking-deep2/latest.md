# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0010-smoking-deep2
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
## Market Research — Kabukicho Survival Map (task-0010-smoking-deep2)

Read-only research per the output contract; no repository files were modified. Existing dataset checked against `app/products/kabukicho_survival_map/data/smoking.json` (17 entries).

---

### Part 1: Boundary quality problem (confirmed)

Checked each of the 17 existing entries against addresses. **2 of the 17 are outside Kabukicho's actual chome boundary** — both are the exact "Ogado/Big Guard near Nishi-Shinjuku" case the task named:

| Entry | Address | Why out of bounds |
|---|---|---|
| 大ガード沿い路上喫煙所 | 西新宿7-1-1 | Nishi-Shinjuku 7-chome, west of Kabukicho's west edge, not Kabukicho 1 or 2-chome. |
| 喫茶室ルノアール(新宿大ガード横店) | 西新宿7-1-1 新宿カレイドビル2F | Same building/block as above — confirmed via Ginza Renoir's own store-locator page. |

Both entries already carry a `gray_zone_note` admitting boundary proximity, but they are addressed in Nishi-Shinjuku, not "near the boundary" — they should be removed from the in-Kabukicho set or explicitly re-tagged `in_kabukicho: false` with a walk-distance note, consistent with the pattern used for toilet entries in task-0009.

The remaining 15 entries all carry addresses in the form 歌舞伎町1-X and are confirmed in-bounds. **All 15 in-bounds entries are in 1-chome — zero are in 2-chome**, confirming the task's stated gap.

Sources: [Ginza Renoir store page](https://www.ginza-renoir.co.jp/shopsearch/shops/tokyo/shinjuku-ku/shinjuku-dai-guard.html)

---

### Part 2: New in-boundary candidates (2-chome)

Searched specifically for all-seats-smoking bars/izakaya/cafés and any new ward-designated outdoor spot within Kabukicho 2-chome. The official Shinjuku Ward public-smoking-facility list ([city.shinjuku.lg.jp](https://www.city.shinjuku.lg.jp/seikatsu/file11_01_00003.html)) shows no additional outdoor designated spot in 2-chome beyond what's already logged (or already flagged as out-of-bounds above) — no new outdoor candidate found.

Four new, distinct, in-boundary, non-duplicate indoor venues were found, all in Kabukicho 2-chome:

```json
[
  {
    "category": "smoking",
    "name": "喫茶 マリエール",
    "lat": 35.6944,
    "lng": 139.7048,
    "description": "歌舞伎町2-2-21(ライオンズマンション歌舞伎町B1F)の昭和30年創業の老舗喫茶店。全席喫煙可、8:30〜23:00営業、定休日なし。",
    "tags": ["indoor", "rain_ok"],
    "reliability_score": 3,
    "source_type": "aggregator",
    "type": "unofficial",
    "gray_zone_note": "喫茶店への注文が必要です。座標は住所ブロックからの概算で、独立した地図APIでの再確認を推奨します。"
  },
  {
    "category": "smoking",
    "name": "ひまわり(タイ料理)",
    "lat": 35.6934,
    "lng": 139.7055,
    "description": "歌舞伎町2-9-15(歌舞伎町ダイヤパレス1F)のタイ料理店。全席喫煙可、17:00〜翌2:00営業(日祝定休)。",
    "tags": ["indoor"],
    "reliability_score": 2,
    "source_type": "aggregator",
    "type": "unofficial",
    "gray_zone_note": "飲食のご注文が必要です。座標は概算、要再確認。"
  },
  {
    "category": "smoking",
    "name": "本格地鶏炭火焼 MORI屋 新宿店",
    "lat": 35.6934,
    "lng": 139.7056,
    "description": "歌舞伎町2-9-18(ライオンズプラザ新宿2F)の宮崎地鶏炭火焼居酒屋。34席、全席喫煙可、月〜木・日18:00〜23:30、金土18:00〜翌3:00。",
    "tags": ["indoor", "crowded"],
    "reliability_score": 3,
    "source_type": "aggregator",
    "type": "unofficial",
    "gray_zone_note": "お食事のご注文が必要です。座標は概算、要再確認。"
  },
  {
    "category": "smoking",
    "name": "コーヒーショップ クール",
    "lat": 35.6918,
    "lng": 139.7065,
    "description": "歌舞伎町2-37-3(マルトモビル2F)の1970年代創業のほぼ24時間営業喫茶店。約40席、全席喫煙可。地元の常連・水商売関係者に長年愛用されている「眠らない喫茶店」として東洋経済オンラインでも紹介されている。",
    "tags": ["indoor", "rain_ok", "crowded"],
    "reliability_score": 3,
    "source_type": "media",
    "type": "unofficial",
    "gray_zone_note": "注文が必要です。深夜・早朝でも開いている点で他の2-chome候補より信頼度が高い(複数の独立記事で確認)。座標は概算、要再確認。"
  }
]
```

**Count reached: 4 new candidates**, short of the 5–8 requested. Additional searches for 2-chome bars/snacks, Korean BBQ, and Chinese restaurants either returned only already-listed 1-chome venues or venues with only *partitioned* (not all-seats) smoking (e.g. 新宿駆け込み餃子 歌舞伎町店, 歌舞伎町1-12-2, has "区切られた喫煙エリア" — excluded, both for partition and for being 1-chome). I did not pad the list further.

---

### Assumptions

- Coordinates for the 4 new candidates are rough estimates based on the eastward position of their block addresses relative to Golden Gai (1-chome's known eastern edge, ~lng 139.7043) and Meiji-dori; they are **not** independently geocoded via a mapping API. Recommend confirming via a geocoding tool before the next data refresh.
- "In Kabukicho" is judged by whether the cited address itself reads 歌舞伎町1-X or 歌舞伎町2-X, not by walking distance to a station — this differs from the toilet-deep-dive's boundary test (which caught entries with non-Kabukicho addresses) and is the correct test here since all 4 new candidates have genuine 歌舞伎町2-X addresses.

### Hypotheses

- H1: The zero-entries-in-2-chome pattern in the existing dataset likely reflects that prior smoking-deep-dive rounds (task-0003 and the original build) searched from a 1-chome-centric set of seed queries (Golden Gai, Cine City Plaza, Ogado) rather than 2-chome-specific terms; targeted 2-chome queries in this round surfaced results almost immediately, suggesting the gap was a search-strategy gap, not a real scarcity of 2-chome venues.
- H2: コーヒーショップ クール is likely the single highest-value new addition — it's the only 24h/near-24h option among the 4, giving 2-chome an equivalent to what 一軒め酒場/お通 already provide in 1-chome for late-night smokers without a purchase-and-leave bar transaction.

### Recommendations

1. Remove or re-flag 大ガード沿い路上喫煙所 and 喫茶室ルノアール(新宿大ガード横店) — both are confirmed at 西新宿7-1-1, outside Kabukicho 1/2-chome. If kept as walkable fallbacks, add `in_kabukicho: false` and a distance note rather than listing them as in-district.
2. Add the 4 new 2-chome candidates (マリエール, ひまわり, MORI屋, コーヒーショップ クール) — they directly close the 2-chome coverage gap the task flagged; all carry cited real addresses and independent-source confirmation of all-seats smoking policy.
3. Geocode all 4 new candidates' coordinates against a mapping API before publishing; current lat/lng are address-block estimates, not measured.
4. Given the low yield in this round (4 of 5–8 requested), treat 2-chome smoking-venue discovery via search as most-but-not-fully exhausted — a further round could specifically target 2-chome host/cabaret-club building lobbies and snack bars, which returned no results here but weren't exhaustively covered.

Sources: [Ginza Renoir 新宿大ガード店](https://www.ginza-renoir.co.jp/shopsearch/shops/tokyo/shinjuku-ku/shinjuku-dai-guard.html), [town-coupon.com マリエール](https://www.town-coupon.com/shop_information/higashishinjuku-mariel), [tabelog マリエール](https://tabelog.com/en/tokyo/A1304/A130401/13088710/), [goo地図 ひまわり](https://map.goo.ne.jp/place/5URF4FHW/), [tabelog ひまわり](https://tabelog.com/en/tokyo/A1304/A130401/13160114/), [favy MORI屋](https://moriyakabukichou.favy.jp/), [hotpepper MORI屋](https://www.hotpepper.jp/strJ000711226/), [shachirin.com コーヒーショップクール](https://shachirin.com/column/2025/11/07/), [kedamatoriko.com コーヒーショップクール](https://www.kedamatoriko.com/entry/coffee/cool/shinjyuku/), [Yahoo!ニュース(東洋経済) コーヒーショップクール](https://news.yahoo.co.jp/articles/084696724124d0a7ff5860e3bf2c4f436ced929d), [新宿区 公衆喫煙所一覧](https://www.city.shinjuku.lg.jp/seikatsu/file11_01_00003.html), [gnavi 新宿駆け込み餃子](https://r.gnavi.co.jp/4wt1e8ck0000/)

