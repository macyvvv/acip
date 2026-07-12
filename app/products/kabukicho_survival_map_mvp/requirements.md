# Requirements

## Functional Requirements

- Kabukicho Survival Map MVP の brief を生成できること
- audience を含めること
- value proposition を含めること
- UGC の扱いを明示すること
- 拡張された map data を deterministic に列挙できること
- 追加データは repo 内 artifact からのみ読み込むこと
- POI detail は confirmed / caution / gray-zone を分離すること
- smartphone first の読みやすさを維持すること
- POI data expansion は incremental であり、実用情報を優先すること
- category summary が mobile-first な初動判断を助けること

## Non-Functional Requirements

- Deterministic output
- No external API calls by default -- this is a cost/scope constraint for an
  early-stage MVP (avoid unnecessary spend on a brief generator), not a
  permanent architectural ban. If a real product need justifies a paid or
  metered external API later, that's a deliberate decision to make and
  document at that time (see `kabukicho_survival_map/requirements.md`'s
  "Superseded requirement" section for the sibling product's real example of
  this exact reversal), not an automatic violation of this rule.
- No mutation of repository OS artifacts
- Data expansion is reviewable and bounded
