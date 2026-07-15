# kabukicho_survival_map_mvp

## Purpose

Issue #34 のための Kabukicho Map Data Expansion を含む最小プロダクトです。

## Mobile UX Notes

- 片手で使いやすいよう、カテゴリ確認を先に行う
- POI詳細は確認情報、注意、gray-zone を分けて読む
- 不確実な情報は disclaimers 付きで扱う
- まずはカテゴリ別の件数を見て、最初の候補を素早く選ぶ

## Entry Point

- `src/kabukicho_survival_map_mvp.py`

## Review Focus

- POI data が実用的に増えているか
- source / caution / last_verified の分離が維持されているか
- スマホで最初の行動がすぐ分かるか
