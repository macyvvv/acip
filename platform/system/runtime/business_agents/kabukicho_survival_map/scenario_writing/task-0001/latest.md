# BUSINESS_AGENT_EXECUTION

business_id: kabukicho_survival_map
role_id: scenario_writing
task_id: task-0001
adapter_mode: execute
resolved_model: claude-sonnet-5
success: true
exit_code: 0

## stdout
Now I have enough grounding. I'll produce the evaluation tag copy and disclaimer text.

## Scenario Writing Output — Kabukicho Survival Map (scenario_writing/task-0001 or next)

Per the role brief: this is read-only content, no files written. Grounded in `market_research/task-0002`'s 6-category POI data and `requirements.md`'s confirmed/caution/gray-zone split.

---

### 1. Tag-based evaluation copy (max 50 chars/line, one template per tag)

**Smoking areas**
| Tag | Comment template |
|---|---|
| `indoor` | 屋内喫煙所・雨天も利用可 |
| `outdoor` | 屋外の喫煙所です |
| `rain_ok` | 屋根あり・雨の日も安心 |
| `crowded` | 混雑しやすい時間帯あり |
| `hidden` | 見つけにくい場所・要注意 |
| `unsafe` | 治安面で注意が必要な場所 |

**Toilets**
| Tag | Comment template |
|---|---|
| `clean` | 清潔と報告されています |
| `dirty` | 汚れが気になるとの報告あり |
| `free` | 無料で利用できます |
| `long_wait` | 混雑時は待ち時間あり |
| `gender_separated` | 男女別トイレです |

**Coin lockers**
| Tag | Comment template |
|---|---|
| `small` | 小型ロッカー(手荷物向け) |
| `medium` | 中型ロッカー(機内持込サイズ) |
| `large` | 大型ロッカー(預け入れサイズ) |
| `suitcase_ok` | スーツケース収納可 |
| `suitcase_too_big` | 大型スーツケースは入りません |

**Lodging / internet cafes**
| Tag | Comment template |
|---|---|
| `shower_available` | シャワーあり(別料金の場合あり) |
| `no_shower` | シャワー設備なし |
| `price_band_budget` | 予算重視の価格帯 |
| `price_band_mid` | 標準的な価格帯 |
| `24h` | 24時間営業 |
| `overnight_friendly` | 深夜〜宿泊利用に対応 |

Each template is ≤50 characters (including Japanese full-width chars, counted per the spec's char cap intent) and is meant to render as a single-line tag chip caption in the UI.

---

### 2. Unofficial-location disclaimer banner

Exact copy per spec, kept in the original structure (warning glyph / status / risk statement), with a localized line added since the product is JP-first per `requirements.md`:

```
⚠ Unofficial Information / Subject to change / Use at your own risk
⚠ 非公式情報・内容は変更される場合があります・ご利用は自己責任でお願いします
```

Usage note for implementation: display this banner on any POI card where `type: "unofficial"` or a populated `gray_zone_note` field is present (per the `Maruhan Pachinko Parlor` and `Café Renoir` entries in market_research/task-0002) — consistent with the existing `##### Gray-zone notes` section and `Safety and Disclaimer` block already in `kabukicho_survival_map_mvp.py`.

