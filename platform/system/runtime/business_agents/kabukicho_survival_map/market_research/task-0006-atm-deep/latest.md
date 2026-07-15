# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: market_research
task_id: task-0006-atm-deep
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
## Market Research — Kabukicho Survival Map (task-0006-atm-deep)

**Business:** kabukicho_survival_map | **Role:** market_research | **Task:** task-0006-atm-deep

Read-only research per the output contract; no repository files were modified.

---

### Facts (grounded in search results, cited)

**Existing dataset gap**
- Current dataset (`task-0002/latest.json`) has exactly 1 ATM entry: a generic "Seven Bank ATM (7-Eleven, Shinjuku/Kabukicho area)" reusing the same coordinates as a convenience-store entry — not a distinct, individually-named location.

**Seven Bank ATMs at 7-Eleven stores confirmed inside Kabukicho**
- Six distinct 7-Eleven addresses inside Kabukicho 1-chome/2-chome were already established with citations in task-0005 (convenience-deep): 1-2-13, 1-19-1 (Toho Bldg), 1-17-2 (Yasukuni-dori), 1-26-6, 2-33-3 (Chuo Ten), and the Kabukicho Nichome Higashi Ten. Seven Bank ATMs are a standard in-store fixture at essentially all 7-Eleven locations nationwide, and the Nichome Higashi store's Seven Bank unit is explicitly documented by name. [pkg.navitime.co.jp/sevenbank](https://pkg.navitime.co.jp/sevenbank/spot/detail?code=0000022792)
- Seven Bank accepts Visa, Mastercard, Amex, UnionPay, JCB, Maestro, Cirrus, Discover, Diners; multilingual (JP/EN/CN/KR) menus; ~¥110 international transaction fee; ¥100,000/withdrawal cap (issuer-dependent). [sevenbank.co.jp](https://www.sevenbank.co.jp/intlcard/index2.html)

**Other bank/institutional ATMs confirmed inside Kabukicho** (via geomedian's dedicated "8 bank/ATM locations in Kabukicho" directory page and individual bank locators)
- MUFG (三菱UFJ銀行) Seibu-Shinjuku Station ATM Corner — Kabukicho 1-30-1. [bank.geomedian.com](https://bank.geomedian.com/shinjuku-ward/d1600021001/)
- MUFG Shinjuku Subnade ATM Corner — Kabukicho 1-chome, Subnade underground mall B1F. [bank.geomedian.com](https://bank.geomedian.com/shinjuku-ward/d1600021001/)
- AEON Bank ATM at Ministop Shinjuku Kabukicho store (2号機/unit 2) — Kabukicho 2-22-1, listed 24h. [map.aeonbank.co.jp](https://map.aeonbank.co.jp/aeonbank/spot/detail?code=0000004370)
- Mizuho Bank ATM at the same Ministop Shinjuku Kabukicho store (1号機/unit 1) — Kabukicho 2-22-1. [shop-sp.www.mizuhobank.co.jp](https://shop-sp.www.mizuhobank.co.jp/b/mizuho_s/info/ae004005/)
- Yucho Bank (ゆうちょ銀行) ATM at FamilyMart Shinjuku Kabukicho store — Kabukicho 2-25-2; hours 00:05–23:55 weekdays and weekends (effectively near-24h). [map.yahoo.co.jp](https://map.yahoo.co.jp/v3/place/apDws4XQnGE)
- Japan Post window ATM, Shinjuku Kabukicho Post Office — Kabukicho 2-41-8; ATM hours weekday 9:00–17:30, Sat 9:00–12:30 (not 24h; teller-adjacent ATM). [map.japanpost.jp](https://map.japanpost.jp/p/search/dtl/300101388000/)
- Japan Post window ATM, Shinjuku Ward Office Post Office — Kabukicho 1-4-1; ATM hours weekday 9:00–17:00 (not 24h). [map.japanpost.jp](https://map.japanpost.jp/p/search/dtl/300101350000/)

**International-card-oriented bank branch bordering (not inside) Kabukicho**
- SMBC Trust Bank Prestia (formerly Citibank Japan, taken over 2015) — Shinjuku Higashiguchi Branch, Shinjuku 3-24-1 (NEWNo・GS Shinjuku 7F), ~700m south of Kabukicho across Yasukuni-dori, not inside the district. ATM hours Mon–Fri 7:00–24:00, Sat 7:00–23:50, Sun 7:00–21:00. SMBC Trust/Prestia cards and cash cards work fee-free at Prestia and SMBC Bank ATMs; no foreign-currency-cash dispensing from the ATM itself (FX exchange is teller-only, weekdays 9:00–15:00, USD/EUR only). [smbctb.co.jp](https://www.smbctb.co.jp/branch/b_shinjuku_higashiguchi.html)

**Excluded as too far / not distinctly Kabukicho**
- MUFG Shinjuku Branch / Shinjuku-dori Branch, Shinjuku 3-30-18 (near Isetan, Shinjuku-sanchome) — ~1km south of Kabukicho, a different Shinjuku sub-area; not included as "bordering." [map.bk.mufg.jp](https://map.bk.mufg.jp/b/bk_mufg/info/BA590096/)
- SMBC (Sumitomo Mitsui Banking Corp, not Trust/Prestia) "Kabukicho Ichibankai CF Loan Contract Corner" (歌舞伎町一番街CFローン契約コーナー) — confirmed as a consumer-loan contract kiosk, not a documented ATM; excluded rather than assumed. [e-map.ne.jp](https://www.e-map.ne.jp/smt/smbcbank/inf/2506040111094/)
- Yucho ATM at Shinjuku Subnade (8:00–21:00) and various Mizuho/MUFG Shinjuku-Station-proper branches — these cluster around JR Shinjuku Station itself, materially south/west of the Kabukicho perimeter already used in prior tasks; excluded to avoid re-padding with non-Kabukicho Shinjuku Station entries (the same issue flagged against the old dataset's 2 convenience-store entries in task-0005).

**Count reached:** 13 distinct, individually-named/addressed ATM entries fully inside Kabukicho, plus 1 bordering entry (Prestia) = **14 total**. This falls short of the requested 15–20 — reported as-is per the no-fabrication instruction rather than padding with unconfirmed locations.

---

### Assumptions

- Seven Bank ATM presence at the 5 non-Nichome-Higashi 7-Eleven addresses (1-2-13, 1-19-1, 1-17-2, 1-26-6, 2-33-3) is inferred from Seven Bank's near-universal in-store deployment policy, not individually confirmed per-store via Seven Bank's own locator — flagged with `reliability_score: 3` accordingly, versus `4` for the Nichome Higashi store where the ATM is directly documented.
- Coordinates are block-level estimates from chome/banchi addresses (consistent with task-0002/0005's stated no-geocoding-API constraint), not independently geocoded.
- "24h" tags for the AEON Bank and Yucho ATMs reflect store-locator-stated hours at time of search, not phone/on-site verified — same caveat logged in prior deep-dive tasks.
- The geomedian directory states "8 bank/ATM locations" in the Kabukicho postal-code area; only 7 could be individually identified and named across sources in this pass (4 from geomedian directly, 3 corroborated via Mizuho/Japan Post's own locators) — the 8th could not be independently confirmed and is not reported.

### Hypotheses

- H1: Because MUFG, Mizuho, and AEON Bank all route their Kabukicho-area ATM presence through combini/station-adjacent "out-of-branch" corners rather than full branches, the product's data model should treat `atm` as frequently co-located with `convenience_store` POIs (as already flagged in task-0005's H2) — a shared `co_located_with` field would avoid duplicate pins for the same physical spot (e.g., Ministop 2-22-1 hosts both a Mizuho and an AEON Bank ATM as two separate machines at one address).
- H2: Japan Post ATMs are the least useful entries for this product's likely audience (nightlife visitors needing cash outside business hours), since both post-office ATMs found are teller-hours-only, not 24h — worth a distinct `hours_type: business_hours_only` tag so the UI doesn't imply late-night availability alongside the 24h Seven Bank/AEON entries.

---

### Proposed POI entries (draft data)

```json
[
  {
    "category": "atm", "name": "Seven Bank ATM — 7-Eleven Kabukicho 1-2-13",
    "lat": 35.6949, "lng": 139.7013,
    "description": "Seven Bank ATM inside 7-Eleven near Seibu-Shinjuku Station, Kabukicho 1-chome. International cards, multilingual menu, ~¥110 fee.",
    "tags": ["24h", "international_card_ok"], "reliability_score": 3,
    "source_type": "inferred", "type": "unofficial"
  },
  {
    "category": "atm", "name": "Seven Bank ATM — 7-Eleven Shinjuku Toho Building Store",
    "lat": 35.6952, "lng": 139.7028,
    "description": "Seven Bank ATM inside 7-Eleven beside the Shinjuku Toho Building (Godzilla Road), Kabukicho 1-19-1.",
    "tags": ["24h", "international_card_ok"], "reliability_score": 3,
    "source_type": "inferred", "type": "unofficial"
  },
  {
    "category": "atm", "name": "Seven Bank ATM — 7-Eleven Yasukuni-dori Store",
    "lat": 35.6944, "lng": 139.7010,
    "description": "Seven Bank ATM inside 7-Eleven at Kabukicho 1-17-2, on Yasukuni-dori.",
    "tags": ["24h", "international_card_ok"], "reliability_score": 3,
    "source_type": "inferred", "type": "unofficial"
  },
  {
    "category": "atm", "name": "Seven Bank ATM — 7-Eleven Kabukicho 1-26-6",
    "lat": 35.6955, "lng": 139.7020,
    "description": "Seven Bank ATM inside 7-Eleven store within Kabukicho 1-chome interior.",
    "tags": ["24h", "international_card_ok"], "reliability_score": 3,
    "source_type": "inferred", "type": "unofficial"
  },
  {
    "category": "atm", "name": "Seven Bank ATM — 7-Eleven Kabukicho 2-chome Chuo Ten",
    "lat": 35.6963, "lng": 139.7038,
    "description": "Seven Bank ATM inside 7-Eleven at Kabukicho 2-33-3, central 2-chome.",
    "tags": ["24h", "international_card_ok"], "reliability_score": 3,
    "source_type": "inferred", "type": "unofficial"
  },
  {
    "category": "atm", "name": "Seven Bank ATM — 7-Eleven Kabukicho Nichome Higashi Ten",
    "lat": 35.6968, "lng": 139.7052,
    "description": "Seven Bank ATM directly documented in-store at this 7-Eleven near Higashi-Shinjuku Station, east Kabukicho 2-chome.",
    "tags": ["24h", "international_card_ok"], "reliability_score": 4,
    "source_type": "official_site", "type": "unofficial"
  },
  {
    "category": "atm", "name": "MUFG Bank — Seibu-Shinjuku Station ATM Corner",
    "lat": 35.6957, "lng": 139.6995,
    "description": "Mitsubishi UFJ Bank out-of-branch ATM corner at Kabukicho 1-30-1, adjacent to Seibu-Shinjuku Station.",
    "tags": ["international_card_ok"], "reliability_score": 4,
    "source_type": "aggregator", "type": "official"
  },
  {
    "category": "atm", "name": "MUFG Bank — Shinjuku Subnade ATM Corner",
    "lat": 35.6942, "lng": 139.6998,
    "description": "Mitsubishi UFJ Bank out-of-branch ATM corner inside the Shinjuku Subnade underground mall, Kabukicho 1-chome, B1F.",
    "tags": ["international_card_ok"], "reliability_score": 4,
    "source_type": "aggregator", "type": "official"
  },
  {
    "category": "atm", "name": "AEON Bank ATM — Ministop Shinjuku Kabukicho (unit 2)",
    "lat": 35.6966, "lng": 139.7044,
    "description": "AEON Bank ATM inside Ministop at Kabukicho 2-22-1; listed 24h by AEON Bank's own locator.",
    "tags": ["24h", "international_card_ok"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "atm", "name": "Mizuho Bank ATM — Ministop Shinjuku Kabukicho (unit 1)",
    "lat": 35.6966, "lng": 139.7044,
    "description": "Mizuho Bank out-of-branch ATM (Ministop Shinjuku Kabukicho-ten 1-goki Shuchosho) at the same Kabukicho 2-22-1 address as the AEON Bank unit — two separate machines, one location.",
    "tags": ["international_card_ok"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "atm", "name": "Yucho Bank ATM — FamilyMart Shinjuku Kabukicho",
    "lat": 35.6960, "lng": 139.7033,
    "description": "Japan Post Bank (Yucho) ATM inside FamilyMart at Kabukicho 2-25-2. Hours 00:05–23:55 daily (effectively near-24h, brief nightly maintenance window).",
    "tags": ["24h"], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "atm", "name": "Japan Post — Shinjuku Kabukicho Post Office ATM",
    "lat": 35.6970, "lng": 139.7055,
    "description": "Window-adjacent Japan Post ATM at Kabukicho 2-41-8, ~2 min walk from Seibu-Shinjuku Station north exit. ATM hours weekday 9:00–17:30, Sat 9:00–12:30 — not 24h.",
    "tags": [], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "atm", "name": "Japan Post — Shinjuku Ward Office Post Office ATM",
    "lat": 35.6944, "lng": 139.7038,
    "description": "Japan Post ATM inside the Shinjuku Ward Office branch post office, Kabukicho 1-4-1. ATM hours weekday 9:00–17:00 only — not 24h.",
    "tags": [], "reliability_score": 4,
    "source_type": "official_site", "type": "official"
  },
  {
    "category": "atm", "name": "SMBC Trust Bank Prestia — Shinjuku Higashiguchi Branch ATM",
    "lat": 35.6903, "lng": 139.7018,
    "description": "Foreign-resident-oriented bank (formerly Citibank Japan, transferred to SMBC Trust/Prestia in 2015), Shinjuku 3-24-1, ~700m south of Kabukicho across Yasukuni-dori — bordering, not inside, the district. ATM hours Mon–Fri 7:00–24:00, Sat 7:00–23:50, Sun 7:00–21:00. Cash-card withdrawal only; no FX cash dispensing from the ATM (currency exchange is teller-only, weekdays 9:00–15:00).",
    "tags": ["international_card_ok"], "reliability_score": 4,
    "source_type": "official_site", "type": "official",
    "gray_zone_note": "Located outside Kabukicho's chome boundaries; included as the nearest dedicated international-banking ATM option, not a within-district entry."
  }
]
```

---

### Recommendations

1. Ship this as **14 entries, not 15–20** — the task instruction explicitly allows reporting fewer with a note; padding further would require either fabricating unconfirmed 7-Eleven ATM presence or re-including out-of-district Shinjuku-Station-proper ATMs already excluded for the same reason in task-0005.
2. Link the two Ministop-2-22-1 entries (AEON Bank + Mizuho Bank) via a shared location/`co_located_with` field rather than treating them as fully independent pins — they're two machines at one physical address (see H1).
3. Add an `hours_type` field distinguishing `24h` (Seven Bank, AEON Bank, Yucho) from `business_hours_only` (both Japan Post window ATMs) — a nightlife-hours product should not visually equate these.
4. Do a single phone/on-site verification pass on the 5 `reliability_score: 3` Seven Bank entries (inferred rather than individually confirmed) before shipping, consistent with the verification-pass recommendation already made in task-0005.
5. Keep the Prestia entry clearly flagged as bordering/outside Kabukicho proper via its `gray_zone_note` — it's the only entry in this set genuinely oriented toward foreign-currency/international banking needs beyond simple cash withdrawal, but it should not be presented as "in Kabukicho."
6. Do not add the "Kabukicho Ichibankai CF Loan Contract Corner" (SMBC) as an ATM — it is a consumer-loan kiosk per its own listing, not a cash machine; flag for exclusion rather than fabrication.

Sources: [pkg.navitime.co.jp/sevenbank](https://pkg.navitime.co.jp/sevenbank/spot/detail?code=0000022792), [sevenbank.co.jp intlcard](https://www.sevenbank.co.jp/intlcard/index2.html), [bank.geomedian.com Kabukicho bank/ATM list](https://bank.geomedian.com/shinjuku-ward/d1600021001/), [map.aeonbank.co.jp Ministop unit 2](https://map.aeonbank.co.jp/aeonbank/spot/detail?code=0000004370), [shop-sp.www.mizuhobank.co.jp Ministop unit 1](https://shop-sp.www.mizuhobank.co.jp/b/mizuho_s/info/ae004005/), [map.yahoo.co.jp Yucho FamilyMart Kabukicho](https://map.yahoo.co.jp/v3/place/apDws4XQnGE), [map.japanpost.jp Shinjuku Kabukicho Post Office](https://map.japanpost.jp/p/search/dtl/300101388000/), [map.japanpost.jp Shinjuku Ward Office Post Office](https://map.japanpost.jp/p/search/dtl/300101350000/), [smbctb.co.jp Shinjuku Higashiguchi branch](https://www.smbctb.co.jp/branch/b_shinjuku_higashiguchi.html), [map.bk.mufg.jp Shinjuku/Shinjuku-dori branch](https://map.bk.mufg.jp/b/bk_mufg/info/BA590096/), [e-map.ne.jp SMBC Kabukicho Ichibankai loan corner](https://www.e-map.ne.jp/smt/smbcbank/inf/2506040111094/)

