# Policy — Frozen

## Goal
GPT Image APIから、LoRA学習に適したキャラクター画像データセットを再現可能に生成する。

## Core Architecture
1. Specification
2. Planning
3. Generation
4. Validation
5. Export

依存方向は上から下のみ。モデル固有処理はAdapterへ隔離する。

## Non-goals
LoRA学習実行、動画生成、Web UI、分散基盤、独自DSL、汎用マルチモデル抽象化、自己学習型Prompt Optimizer。

## Quality
画像単体品質、一貫性、学習上不要な相関、分布充足を別々に評価する。
自動評価は補助。最終採択は監査可能なルールと人手レビューを併用する。

## Data
全生成物はcontent hash、仕様version、prompt、API設定、採否、理由を保持する。
raw生成物は不変。加工・採択・exportは派生物として分離する。

## Change Control
ゴールと五層構造は凍結。変更可能なのはschemaの後方互換追加、Adapter、評価閾値、sampling policy、character specification。
