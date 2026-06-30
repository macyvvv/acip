# Architecture

## Components

- `src/kabukicho_survival_map_mvp.py`: brief を組み立てる
- `data/kabukicho_map_places.json`: 拡張された map data を保持する
- `tests/test_kabukicho_survival_map_mvp.py`: 挙動を検証する

## Data Flow

Repository data artifact -> product brief generator -> markdown output

## Decision Flow

- Scope, audience, value proposition, and UGC boundary are fixed in the artifact.
- Map data expansion is bounded by the repository-local JSON asset.
- Missing repository context is not inferred.
