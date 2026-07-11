# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0009-toilet-deep2
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
## Market Research — Kabukicho Survival Map (task-0009-toilet-deep2)

**Business:** kabukicho_survival_map | **Role:** market_research | **Task:** task-0009-toilet-deep2

Read-only research per the output contract; no repository files were modified.

---

### Part 1: Boundary quality problem (primary finding)

Checking each of the 15 existing toilet entries against the stated Kabukicho 1/2-chome box (Yasukuni-dori south / Shokuan-dori north / Meiji-dori east / Seibu-Shinjuku–Odakyu area west), **5 of the 15 existing entries are outside Kabukicho's actual chome boundaries** and should be removed or explicitly re-tagged as "near Kabukicho, not in it":

| Entry | Why it's out of bounds |
|---|---|
| 新宿駅東南口公衆便所 (Shinjuku Station Southeast Exit) | South of Yasukuni-dori, at the JR Shinjuku Station south concourse — Shinjuku 3-chome/Station area, not Kabukicho. |
| 新宿西口地下第一公衆便所 (Shinjuku West Exit Underground No.1) | West side of Shinjuku Station, across from Odakyu — outside the west boundary entirely (this is the example the task itself flagged). |
| 新宿サブナード地下トイレ (Subnade underground arcade) | Subnade runs under the JR Shinjuku Station East Exit concourse, south of Yasukuni-dori — station-area, not Kabukicho chome. |
| 新宿駅東口「フードポケット」トイレ (East Exit Food Pocket) | Basement of JR Shinjuku Station East Exit near Lumine Est — same station-area problem as above. |
| 新宿三丁目駅 地下通路トイレ (Shinjuku-sanchome Station underground passage) | East of Meiji-dori, at the Marunouchi Line Shinjuku-sanchome station — outside the east boundary (the task's other named example). |

Entries confirmed **in-bounds** (verified by cited address, all sit inside Kabukicho 1 or 2-chome): 新宿遊歩道公園(四季の道)公衆トイレ, 東急歌舞伎町タワー トイレ / 2階トイレ, 西武新宿駅前公衆便所 (station sits at Kabukicho 1-30-1, right on the stated west edge), 大久保公園トイレ, Haijia 1階トイレ, 新宿区役所本庁舎1階トイレ (Kabukicho 1-4-1), 四季の路トイレ, TOHOシネマズ新宿 3階トイレ (Kabukicho 1-19-1), MEGAドン・キホーテ新宿歌舞伎町店 トイレ (Kabukicho 1-16-5). [city.shinjuku.lg.jp](https://www.city.shinjuku.lg.jp/kusei/soumu01_000110.html), [shinjuku.mypl.net](https://shinjuku.mypl.net/kosodate_barrier/00000000069/)

### Part 2: New in-boundary candidates

I searched specifically for pachinko-hall toilets, drugstore/konbini toilets, hotel lobby toilets, game-center toilets, and additional ward park toilets strictly inside Kabukicho 1/2-chome. Most leads dead-ended:

- **Kabukicho Park (歌舞伎町公園)**, Kabukicho 1-chome — confirmed to exist as a small ward park, but no source confirms it has a public toilet. Not included (unverifiable).
- **GiGO Shinjuku Kabukicho** (game center, Kabukicho 1-21-1) — no source states toilet availability/policy for non-customers.
- **Matsumoto Kiyoshi Shinjuku Kabukicho-ten** (drugstore, Kabukicho 1-17-10) — 24h store, but no source confirms restroom-lending policy, and the general finding from task-0004 is that Kabukicho retail generally does *not* lend restrooms.

Two candidates cleared the bar for "distinct, citable, in-boundary" but only at weak/gray-zone confidence:

```json
[
  {
    "category": "toilet",
    "name": "エスパス日拓 新宿歌舞伎町店 トイレ (Espace Nittaku Shinjuku Kabukicho pachinko hall toilet)",
    "lat": 35.6949, "lng": 139.6998,
    "description": "In-store customer toilet at a large pachinko hall, Kabukicho 1-23-3, ~0 min from Seibu-Shinjuku Station front exit.",
    "tags": ["free"],
    "reliability_score": 2,
    "source_type": "aggregator",
    "type": "unofficial",
    "gray_zone_note": "Store-specific toilet policy is not independently confirmed; based on the general Japan-wide norm that large pachinko halls tolerate toilet-only visits (per Yahoo Chiebukuro discussion), not a store-verified statement. Staff discretion applies."
  },
  {
    "category": "toilet",
    "name": "新宿プリンスホテル B1トイレ (Shinjuku Prince Hotel B1 toilet)",
    "lat": 35.6949, "lng": 139.7002,
    "description": "Basement-level hotel toilet with nursing room and diaper table, Kabukicho 1-1-2, directly above Seibu-Shinjuku Station.",
    "tags": ["clean"],
    "reliability_score": 1,
    "source_type": "forum",
    "type": "unofficial",
    "gray_zone_note": "Non-guest access is explicitly uncertain — a Yahoo Chiebukuro user asked whether non-guests can use it and no definitive answer was found; hotel lobby norms mean staff could turn away non-guests. Do not present as a reliable fallback."
  }
]
```

**Count reached: 2 new candidates**, both gray-zone/low-confidence — short of the requested 5–8. I did not pad the list further; remaining plausible categories (individual host/cabaret-club buildings, other pachinko halls like Espace Nittaku's sister branches, hotel lobbies) either have no findable restroom-policy statement at all, or would require an on-site/phone check rather than search, matching the same wall hit in the original toilet-deep dive (task-0004).

---

### Assumptions

- Coordinates are approximate from cited street-block addresses, not geocoded via a mapping API (consistent with prior deep-dives).
- "Kabukicho 1/2-chome" boundary interpretation follows the task's stated streets; I did not independently verify the ward's exact chome polygon, only that the 5 flagged entries' addresses are in adjacent chome (Shinjuku 3-chome / Nishi-Shinjuku / Shinjuku Station concourse), not Kabukicho 1 or 2.
- Tokyu Kabukicho Tower's 2F toilet is now reported as authenticated/customer-only access rather than fully open to the public — this doesn't create a boundary problem (it's in-bounds) but is worth flagging as a correction to the existing entry's access description in a future pass, separate from this task's scope.

### Hypotheses

- H1: The 5 out-of-boundary entries likely entered the dataset because they're genuinely useful *fallbacks* a Kabukicho visitor would walk to (a legitimate product concern), but conflating "useful nearby" with "in Kabukicho" is what created the quality problem the task flagged — the fix is a `location_note: "outside Kabukicho chome, X min walk"` field, not necessarily deletion.
- H2: The near-total absence of new citable in-boundary toilets (beyond the original 15) suggests the toilet-deep-dive (task-0004) already found the practical ceiling for search-based discovery in this footprint; further gains would need on-site fieldwork (walking Kabukicho 1/2-chome and checking pachinko halls/game centers directly), not another search round.

### Recommendations

1. Reclassify or remove the 5 out-of-boundary entries (新宿駅東南口, 新宿西口地下第一, 新宿サブナード, フードポケット, 新宿三丁目駅) from the "in Kabukicho" toilet set; if kept as fallback options, add an explicit `in_kabukicho: false` / distance note rather than listing them alongside true in-boundary entries.
2. Do not add the 2 new gray-zone candidates (Espace Nittaku, Shinjuku Prince Hotel) as reliable POIs without a manual on-site/phone verification pass — both carry `reliability_score` ≤2 and unresolved access-policy uncertainty.
3. Given the low yield of this second search round, treat further toilet-specific web-search tasks for Kabukicho as exhausted; if more coverage is wanted, commission an on-site fieldwork task instead (walk the two chome, check remaining pachinko halls/game centers/host-club building lobbies directly).
4. Separately from this task's scope: verify Tokyu Kabukicho Tower 2F's current customer-only/authenticated access policy before the next data refresh, since it may no longer function as an open public toilet as originally logged.

Sources: [hostrank.jp/kabukicho-toilet-guide](https://hostrank.jp/blog/kabukicho-toilet-guide), [city.shinjuku.lg.jp (公園トイレ・公衆トイレ)](https://www.city.shinjuku.lg.jp/seikatsu/index15_07.html), [city.shinjuku.lg.jp (歌舞伎町公園)](https://www.city.shinjuku.lg.jp/seikatsu/midori01_002115.html), [city.shinjuku.lg.jp (大久保公園)](https://www.city.shinjuku.lg.jp/seikatsu/midori02_000105.html), [daily-shinjuku.tokyo toilet guide 2026](https://daily-shinjuku.tokyo/2026/02/03/shinjuku-toilet-guide/), [mapion.co.jp (Espace Nittaku Shinjuku Kabukicho-ten address)](https://www.mapion.co.jp/phonebook/M03004/13104/21330891177/), [Yahoo!知恵袋 (パチンコ屋 トイレ借用)](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11248028916), [Yahoo!知恵袋 (新宿プリンスホテル 非宿泊客トイレ)](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11297814491), [princehotels.co.jp (館内のご案内)](https://www.princehotels.co.jp/shinjuku/facility/), [nta.co.jp (新宿プリンスホテル施設)](https://www.nta.co.jp/yado/shisetsu/3628-306.htm)

