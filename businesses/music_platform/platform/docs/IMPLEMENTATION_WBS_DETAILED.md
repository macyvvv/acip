# IMPLEMENTATION_WBS_DETAILED

## Purpose

本ドキュメントは、`music_platform` の全機能（F1-F32）を実装完了まで進めるための
詳細WBS正本である。

前提:

- 機能の取捨選択は行わない（全機能実装前提）
- 優先順位のための学習は行わない
- 実装改善のための学習（計測 -> 知見化 -> 反映）は必須で行う
- DevOps / DataOps / MLOps を中核ロールとして実行する

## Planning Rules

1. 優先順位ではなく「依存関係」と「実装可能性」で順序を決める。
2. すべてのWBS項目に Owner / Input / Output / DoD / Dependency を持たせる。
3. 因果断定が必要な分析はUIに出さない（不確実性文言を必須化）。
4. 4週間単位で実装進捗と運用品質をレビューする。
5. 各機能は「学習可能性」を満たす計測イベントを実装する。
6. 学習で得た知見は次スプリントで必ず反映可否を判定する。

## WBS Structure

- WBS-0: Program Governance
- WBS-1: DevOps Foundation
- WBS-2: DataOps Foundation
- WBS-3: MLOps Safety Layer
- WBS-4: Shared Product Capabilities
- WBS-5: Participant Features
- WBS-6: Organizer Features
- WBS-7: Post-Event and Retention Features
- WBS-8: Release, SLO, and Operations
- WBS-9: Learning and Knowledge Reuse

## WBS-0 Program Governance

### WBS-0.1 Backlog Lock

- Owner: DevOps
- Input: `USER_VALUE_ANALYTICS_CANON.md` の F1-F32
- Output: 実装対象一覧（32機能）
- Dependency: なし
- DoD: 実装対象が32件で固定され、欠番なし

### WBS-0.2 Interface Contract Freeze

- Owner: DevOps
- Input: 機能台帳、既存DBスキーマ
- Output: API/バッチI/O契約
- Dependency: WBS-0.1
- DoD: 全機能が参照するI/O契約が定義済み

### WBS-0.3 Sprint Cadence Setup

- Owner: DevOps
- Input: チーム稼働枠
- Output: 4週間スプリント定義
- Dependency: WBS-0.1
- DoD: スプリント開始/終了条件が文書化済み

## WBS-1 DevOps Foundation

### WBS-1.1 Batch Pipeline Baseline

- Owner: DevOps
- Input: DB、既存ドキュメント
- Output: 日次/週次バッチジョブ
- Dependency: WBS-0.2
- DoD: 自動実行・再実行・失敗通知が動作

### WBS-1.2 Release Gate Implementation

- Owner: DevOps
- Input: Data/MLゲート条件
- Output: 公開判定ゲート
- Dependency: WBS-2.2, WBS-3.2
- DoD: ゲート未達時は自動で公開停止

### WBS-1.3 Rollback and Fallback

- Owner: DevOps
- Input: 前回正常版成果物
- Output: フォールバック運用
- Dependency: WBS-1.1
- DoD: 障害時に前回正常版へ自動切替

### WBS-1.4 Observability Stack

- Owner: DevOps
- Input: 実行ログ、メタデータ
- Output: 監視ダッシュボード
- Dependency: WBS-1.1
- DoD: 鮮度/失敗率/遅延/アラートが可視化

## WBS-2 DataOps Foundation

### WBS-2.1 Data Quality Gate

- Owner: DataOps
- Input: `bandoff_research_merged.db`
- Output: 品質判定ルール（欠損・重複・鮮度）
- Dependency: WBS-0.2
- DoD: 主要テーブルの品質閾値が定義済み

### WBS-2.2 Analysis-Ready Views

- Owner: DataOps
- Input: `merged_events`, `merged_songs`
- Output: 機能別参照ビュー
- Dependency: WBS-2.1
- DoD: F1-F32の参照データ要件が満たされる

### WBS-2.3 Confounder Register Operation

- Owner: DataOps
- Input: 解析結果
- Output: 交絡要因レジスタ（週次更新）
- Dependency: WBS-2.2
- DoD: 主要交絡要因が毎週更新される

### WBS-2.4 Segment Data Sufficiency Check

- Owner: DataOps
- Input: 4セグメント定義
- Output: セグメント別サンプル充足レポート
- Dependency: WBS-2.2
- DoD: 各セグメントの検証可否が明示される

## WBS-3 MLOps Safety Layer

### WBS-3.1 Drift Monitor Setup

- Owner: MLOps
- Input: 特徴量分布
- Output: PSI/JSD等の監視指標
- Dependency: WBS-2.2
- DoD: 週次ドリフトレポート自動生成

### WBS-3.2 Go/Conditional/No-Go Policy

- Owner: MLOps
- Input: ドリフト結果、品質結果
- Output: 公開可否判定
- Dependency: WBS-3.1, WBS-2.1
- DoD: 判定基準が運用で実行可能

### WBS-3.3 Uncertainty Copy Templates

- Owner: MLOps
- Input: 分析カード仕様
- Output: 断定回避文言テンプレ
- Dependency: WBS-3.2
- DoD: 全分析表示に不確実性文言を適用

### WBS-3.4 Segment Error Monitoring

- Owner: MLOps
- Input: セグメント別出力
- Output: 誤差差分レポート
- Dependency: WBS-2.4
- DoD: 4セグメント差分が可視化

## WBS-4 Shared Product Capabilities

### WBS-4.1 Identity and Profile Primitives

- Owner: DevOps
- Input: 参加者/主催者要件
- Output: プロファイル基盤（担当楽器、経験等）
- Dependency: WBS-1.1
- DoD: 主要プロフィール項目が保存可能

### WBS-4.2 Notification Service

- Owner: DevOps
- Input: 直前アラート要件
- Output: 通知基盤
- Dependency: WBS-1.4
- DoD: 送信成功率・再送が監視可能

### WBS-4.3 Timeline and Activity Log

- Owner: DevOps
- Input: 進捗履歴
- Output: 時系列イベントログ
- Dependency: WBS-1.1
- DoD: F23/F26など共通機能で再利用可能

### WBS-4.4 Feature Flags for Controlled Rollout

- Owner: DevOps
- Input: 段階公開計画
- Output: 機能単位の公開制御
- Dependency: WBS-1.2
- DoD: セグメント単位でON/OFF制御可能

## WBS-5 Participant Features

対象機能: F1, F2, F3, F4, F9, F10, F11, F12, F13, F14, F15, F20, F24, F25, F28, F30

### WBS-5.1 Discover Bundle

- Owner: DevOps
- Scope: F1/F9/F10/F11/F12/F13
- Dependency: WBS-2.2, WBS-4.1
- DoD: 参加判断系UIが4セグメントで表示可能

### WBS-5.2 Entry Bundle

- Owner: DevOps
- Scope: F2/F3/F14/F15
- Dependency: WBS-5.1, WBS-4.2
- DoD: 初回連絡からエントリーまで一貫導線が動作

### WBS-5.3 Mid-to-Day Bundle

- Owner: DevOps
- Scope: F4/F20/F24/F25
- Dependency: WBS-4.3
- DoD: 中盤〜当日の準備支援が機能

### WBS-5.4 Retention Bundle

- Owner: DevOps
- Scope: F28/F30
- Dependency: WBS-5.3
- DoD: 終了後の再参加導線が機能

## WBS-6 Organizer Features

対象機能: F5, F6, F7, F16, F17, F18, F19, F21, F22, F27, F29, F31

### WBS-6.1 Setup Bundle

- Owner: DevOps
- Scope: F5/F16/F17
- Dependency: WBS-2.2
- DoD: 募集設計・テンプレ支援が機能

### WBS-6.2 Momentum Bundle

- Owner: DevOps
- Scope: F6/F18/F19/F21/F22
- Dependency: WBS-4.3, WBS-4.2
- DoD: 未成立救済の優先行動が提示可能

### WBS-6.3 Day-of Bundle

- Owner: DevOps
- Scope: F7/F27
- Dependency: WBS-4.2
- DoD: 直前アラートと欠損通知が稼働

### WBS-6.4 Review Bundle

- Owner: DevOps
- Scope: F29/F31
- Dependency: WBS-6.2
- DoD: 主催振り返りとテンプレ更新提案が稼働

## WBS-7 Shared and Platform Features

対象機能: F8, F23, F26, F32

### WBS-7.1 Cross-Segment Timeline

- Owner: DevOps
- Scope: F23
- Dependency: WBS-4.3
- DoD: 全セグメントで進捗タイムライン閲覧可能

### WBS-7.2 Emergency Hub

- Owner: DevOps
- Scope: F26
- Dependency: WBS-4.2
- DoD: 当日変更の影響通知が動作

### WBS-7.3 Improvement Notes Automation

- Owner: DataOps
- Scope: F8
- Dependency: WBS-2.2, WBS-6.4
- DoD: 改善候補が構造化出力される

### WBS-7.4 Community Health Report

- Owner: DataOps
- Scope: F32
- Dependency: WBS-2.3, WBS-3.4
- DoD: 健全性指標が週次で更新される

## WBS-8 Release and Operations

### WBS-8.1 Staged Rollout

- Owner: DevOps
- Input: 各Bundle完成
- Output: 内部→限定→全体公開
- Dependency: WBS-1.2, WBS-4.4
- DoD: 各段階で障害なく公開完了

### WBS-8.2 KPI Instrumentation

- Owner: DataOps
- Input: 体験KPI定義
- Output: KPI計測クエリ
- Dependency: WBS-5, WBS-6, WBS-7
- DoD: KPIが週次で追跡可能

### WBS-8.3 Incident Drill

- Owner: DevOps
- Input: 障害シナリオ
- Output: 復旧訓練結果
- Dependency: WBS-1.3
- DoD: 復旧SLOを満たす

### WBS-8.4 Monthly Ops Review

- Owner: DevOps
- Input: KPI、ドリフト、品質レポート
- Output: 次月の実行計画
- Dependency: WBS-8.2
- DoD: 改善アクションが起票済み

## WBS-9 Learning and Knowledge Reuse

目的: 実装を進めるほど学習可能になり、得られた知見を次フェーズへ反映する。

### WBS-9.1 Instrumentation Completeness Audit

- Owner: DevOps
- Input: 全機能仕様（F1-F32）
- Output: 計測イベント実装率レポート
- Dependency: WBS-5, WBS-6, WBS-7
- DoD: 全機能で最低1つの行動イベントと結果イベントが計測される

### WBS-9.2 Insight Extraction Pipeline

- Owner: DataOps
- Input: KPI計測結果、セグメント別行動ログ
- Output: `insight_register`（有効/無効仮説、再現条件、適用範囲）
- Dependency: WBS-8.2, WBS-9.1
- DoD: 4週間ごとに知見が更新される

#### WBS-9.2 Spec: insight_register

`insight_register` は「分析メモ」ではなく、次スプリントの実装判断に使う構造化レジスタとする。

必須カラム定義:

1. `insight_id` (TEXT): 一意ID。形式 `INS-YYYYMM-XXX`
2. `captured_at_utc` (TEXT): 抽出日時
3. `owner_role` (TEXT): `dataops|mlops|devops`
4. `segment_scope` (TEXT): `participant_beginner|participant_repeater|organizer_beginner|organizer_repeater|cross_segment`
5. `feature_scope` (TEXT): 対象機能ID。複数時は `F1,F6` 形式
6. `journey_stage` (TEXT): `discover|entry|build|run|review`
7. `hypothesis` (TEXT): 検証した仮説
8. `observation` (TEXT): 観測事実（集計結果）
9. `evidence_query_ref` (TEXT): 参照SQLまたはレポートID
10. `sample_size` (INTEGER): 対象母数
11. `effect_direction` (TEXT): `positive|negative|mixed|none`
12. `effect_magnitude` (REAL): 効果量（標準化値または相対差）
13. `confidence_level` (TEXT): `low|medium|high`
14. `confounder_notes` (TEXT): 交絡メモ
15. `validity_status` (TEXT): `adopt|watch|reject|expired`
16. `valid_until_utc` (TEXT): 有効期限
17. `recommended_action` (TEXT): 推奨アクション
18. `implementation_ticket_ref` (TEXT): 実装チケットID
19. `rollback_condition` (TEXT): 反映後に戻す条件
20. `notes` (TEXT): 補足

SQLite DDL（推奨）:

```sql
CREATE TABLE IF NOT EXISTS insight_register (
	insight_id TEXT PRIMARY KEY,
	captured_at_utc TEXT NOT NULL,
	owner_role TEXT NOT NULL,
	segment_scope TEXT NOT NULL,
	feature_scope TEXT NOT NULL,
	journey_stage TEXT NOT NULL,
	hypothesis TEXT NOT NULL,
	observation TEXT NOT NULL,
	evidence_query_ref TEXT NOT NULL,
	sample_size INTEGER NOT NULL,
	effect_direction TEXT NOT NULL,
	effect_magnitude REAL,
	confidence_level TEXT NOT NULL,
	confounder_notes TEXT,
	validity_status TEXT NOT NULL,
	valid_until_utc TEXT,
	recommended_action TEXT NOT NULL,
	implementation_ticket_ref TEXT,
	rollback_condition TEXT,
	notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_insight_validity
	ON insight_register(validity_status, valid_until_utc);

CREATE INDEX IF NOT EXISTS idx_insight_segment_feature
	ON insight_register(segment_scope, feature_scope);
```

入力品質ルール:

1. `sample_size < 30` は原則 `watch` まで（`adopt` 禁止）
2. `confidence_level = low` は `implementation_ticket_ref` を空にする
3. `confounder_notes` が空なら `adopt` 不可
4. `valid_until_utc` を超えたレコードは自動的に `expired` へ遷移

更新サイクル:

1. 週次: 新規知見追加、既存知見の状態更新
2. 4週次: `adopt/watch/reject` 棚卸し、期限更新
3. スプリント計画時: `adopt` のみ実装候補として受理

状態遷移:

1. `watch -> adopt`: サンプル充足 + 交絡確認 + 再現確認
2. `watch -> reject`: 効果消失または逆転
3. `adopt -> expired`: 有効期限超過
4. `adopt -> reject`: 反映後に悪化指標が閾値超過

実装連携ルール:

1. `adopt` は必ず `implementation_ticket_ref` を持つ
2. チケットには `rollback_condition` を転記する
3. リリース後は 2週間以内に再評価し、`notes` に結果追記

最小運用レポート（週次）:

1. 新規知見件数（segment別）
2. `adopt/watch/reject/expired` の件数
3. 実装チケット連携率
4. 期限切れ放置件数

### WBS-9.3 Learning Validity Gate

- Owner: MLOps
- Input: `insight_register`, ドリフト/誤差差分レポート
- Output: 知見の有効性判定（Adopt / Watch / Reject）
- Dependency: WBS-3.1, WBS-3.4, WBS-9.2
- DoD: 各知見に有効期限と適用条件が付与される

判定基準（運用規定）:

1. Adopt
	- `sample_size >= 30`
	- `confidence_level in (medium, high)`
	- 主要交絡に対する説明がある
	- 2回以上の観測で方向一致
2. Watch
	- サンプル不足、または交絡整理待ち
3. Reject
	- 再現性なし、または悪化方向
4. Expired
	- `valid_until_utc` 超過で自動遷移

### WBS-9.4 Reuse-to-Implementation Handoff

- Owner: DevOps
- Input: Adopt判定済み知見
- Output: 実装変更チケット（UI/通知/導線/テンプレ更新）
- Dependency: WBS-9.3
- DoD: Adopt知見が次スプリント計画へ反映される

### WBS-9.5 Segment-Specific Playbook Update

- Owner: DataOps
- Input: 4セグメント別効果差
- Output: セグメント別運用プレイブック
- Dependency: WBS-9.2, WBS-9.3
- DoD: 初心者/リピーター、主催者/参加者それぞれの推奨介入が更新される

### WBS-9.6 Knowledge Drift Review

- Owner: MLOps
- Input: 既存知見、直近データ分布
- Output: 失効知見リストと更新提案
- Dependency: WBS-3.1, WBS-9.2
- DoD: 古い知見が運用に残留しない

## Milestones

- M1: Foundation Complete (WBS-1,2,3)
- M2: Participant Bundles Complete (WBS-5)
- M3: Organizer Bundles Complete (WBS-6)
- M4: Shared Features Complete (WBS-7)
- M5: Full Operationalization (WBS-8)
- M6: Learning Loop Operationalized (WBS-9)

## Critical Path

1. WBS-0.2 -> WBS-1.1 -> WBS-2.2 -> WBS-3.2
2. WBS-4.1/4.2/4.3 -> WBS-5.x and WBS-6.x
3. WBS-1.2 + WBS-8.1 for safe public rollout
4. WBS-8.2 -> WBS-9.2 -> WBS-9.3 -> WBS-9.4 for knowledge reuse

## Acceptance Criteria

1. F1-F32 がすべて実装済み
2. Data/ML/Opsゲートが運用されている
3. 体験KPIが継続計測されている
4. 障害時フォールバックが実証済み
5. 学習ループ（知見抽出/有効性判定/再実装反映）が運用されている
