# Requirements

## Functional

- Launch brief を生成できること
- ターゲット audience を含めること
- value proposition を含めること
- publish checklist を含めること

## Non-Functional

- Deterministic output
- No external API calls by default -- this is a cost/scope constraint for an
  early-stage generator (avoid unnecessary spend), not a permanent
  architectural ban. A later real product need can justify a paid/metered
  external API as a deliberate, documented decision (see
  `kabukicho_survival_map/requirements.md`'s "Superseded requirement"
  section for the sibling product's real example of this exact reversal).
