# IMPLEMENTATION_AND_DISCOVERY_ROADMAP

## Purpose

`music_platform` の現在目標を次の二軸で同時達成するための実行ロードマップ。

1. サイト機能をWBSに沿って実装完了まで進める（Feature Delivery Axis）
2. その実装を安全・有効にするため、データから何が見出せるかを継続的に検証する（Data Discovery Axis）

本ロードマップは DevOps / DataOps / MLOps を中核に進める。

## Scope

対象:

- `USER_VALUE_ANALYTICS_CANON.md` で定義した機能台帳（F1-F32）の全実装
- 交絡・分布偏りを前提とした分析運用
- 安全なリリース運用（品質ゲート、フォールバック、監視）

対象外:

- 因果断定が必要な意思決定の確定

## North Star

- 数字の最適化ではなく、ユーザー行動の改善を最優先する。
- すべての実装機能は「行動変化」と「体験KPI」で評価する。
- 不確実性が高い分析は表示を制限する（Fail Safe）。

## Operating Model

二軸は並列ではなく、毎スプリントで接続された1ループとして運用する。

1. Data Discovery: 仮説と検証結果を更新
2. Feature Delivery: WBSに沿って実装を進める
3. Delivery: 安全に実装・公開
4. Measurement: 行動変化を計測
5. Re-plan: 依存関係と完了率で次スプリント計画を更新

## Sequencing Framework (Feature Axis)

機能採用の可否ではなく、実装順序を次で決める。

1. 依存関係（前提機能/基盤の有無）
2. 実装可能性（データ入出力、API契約、運用準備）
3. 運用安全性（ゲート、監視、フォールバック準備）
4. セグメント公平性（4セグメントで表示可能か）

着手条件:

1. 成功シグナルが定義されている
2. 4週間以内に検証可能
3. 失敗時フォールバックがある
4. 因果断定なしで価値提供できる

## Discovery Framework (Data Axis)

DataOps / MLOps が毎スプリントで以下を更新する。

1. 交絡因子リスト（新增/変更）
2. 分布シフト指標（PSI/JSD/主要特徴カバレッジ）
3. セグメント別性能差（初心者/リピーター、主催者/参加者）
4. 公開可否判定（Go / Conditional Go / No-Go）

## Role Plan

### DataOps

責務:

- データ品質ゲート運用（欠損、重複、鮮度、整合）
- 交絡管理と層別ルール更新
- 解析可能ビュー定義

成果物:

- `data_readiness_report`（週次）
- `confounder_register`（週次更新）
- `analysis_ready_views`（SQL定義）

DoD:

- 重要カラムの品質が閾値内
- セグメント別に最低サンプル数を満たす
- 検証クエリが再実行可能

### MLOps

責務:

- 係数変動/ベクトル偏り監視
- モデル/スコアの可否判定
- 不確実性表示の一貫性維持

成果物:

- `drift_report`（週次）
- `model_gate_decision`（Go/Conditional/No-Go）
- `explanation_template`（UI用）

DoD:

- ドリフト監視が稼働
- セグメント別誤差差分の可視化完了
- No-Go時フォールバック経路が検証済み

### DevOps

責務:

- 分析出力パイプライン実装
- リリースゲートとロールバック
- 監視/アラート/SLO運用

成果物:

- 日次/週次バッチ
- リリースゲート定義
- 運用ダッシュボード（鮮度・品質・失敗率）

DoD:

- ジョブ失敗時の前回正常版継続が機能
- 主要アラートが通知される
- 監査情報（run_id/version/timestamp）を保持

## 12-Week Roadmap

### Phase 0 (Week 1-2): Foundation

目標: 二軸を回すための最低運用基盤を作る

- DataOps
  - 品質ゲート定義（欠損、重複、鮮度）
  - 交絡因子初版を確定
- MLOps
  - ドリフト監視指標を確定
  - Go/No-Go暫定ルール策定
- DevOps
  - 週次バッチ骨組み
  - run metadata保存とアラート初版

Exit Criteria:

1. 週次で `data_readiness_report` が自動生成
2. Go/No-Go判定が毎週出る
3. 失敗時に前回正常版へ切替可能

### Phase 1 (Week 3-5): First Decision Loop

目標: F1-F32全実装に向けたWBSシーケンスを確定

- DataOps
  - 各機能に必要なデータ可用性を評価
  - 不足データと代替指標を提示
- MLOps
  - 各機能の不確実性レベルを評価
  - 表示制限ルールを付与
- DevOps
  - WBSバンドル単位の計測イベント設計
  - Feature flag運用開始

Exit Criteria:

1. 全機能の実装順序（依存関係ベース）が確定
2. 各機能の成功シグナル定義完了
3. 計測イベントが実装済み

### Phase 2 (Week 6-9): Build and Measure

目標: 優先上位機能を実装し、体験KPIで評価

- DataOps
  - 効果検証クエリの標準化
  - セグメント別比較レポート運用
- MLOps
  - 係数変動監視を反映した表示制御
  - Conditional Go機能の配信制限
- DevOps
  - 段階リリース（内部→限定公開→全体）
  - フォールバック訓練（障害ドリル）

Exit Criteria:

1. 初回実装機能の体験KPIが計測可能
2. セグメント別効果差が可視化
3. 重大障害時の復旧手順が実証済み

### Phase 3 (Week 10-12): Scale and Re-prioritize

目標: 効果のあった機能を拡張し、次サイクルへ接続

- DataOps
  - 検証結果を機能台帳へ反映
  - 無効仮説/有効仮説の更新
- MLOps
  - しきい値調整と再評価
  - 説明文テンプレの改善
- DevOps
  - 運用SLOレビュー
  - 自動化対象の拡張

Exit Criteria:

1. 次サイクルの優先順位再計算完了
2. 価値が低い機能候補を棚卸し
3. 監視/ゲートが運用定着

## Core Metrics

### Feature Axis Metrics

1. 初回行動転換率
2. 未成立曲放置期間
3. 直前救済対応件数
4. 初参加30日再参加率
5. 主催者継続開催率

### Discovery Axis Metrics

1. データ品質合格率
2. ドリフト警戒/重大件数
3. Go/Conditional/No-Go比率
4. セグメント別誤差差分
5. フォールバック発動率

## Release Gate (Mandatory)

新規分析機能を公開するには全ゲート通過が必要。

1. Data Gate: 品質・鮮度合格
2. ML Gate: 可否判定が Go または Conditional Go
3. Ops Gate: 監視とロールバック有効
4. UX Gate: 断定回避文言と不確実性表示あり

1つでも未達なら公開せず、前回正常版を継続する。

## Next Action

1. `IMPLEMENTATION_WBS_DETAILED.md` を基準に全機能の実装計画を確定
2. WBS-1/2/3（基盤）を先行実装
3. WBS-5/6/7を依存関係順に実装
4. WBS-9.2 の `insight_register` 仕様に基づき、知見抽出と再実装連携を運用開始
