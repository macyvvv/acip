# SITEMAP

## 1. Purpose

本書は `music_platform` の情報設計正本である。
対象は `USER_VALUE_ANALYTICS_CANON.md` の F1-F32 機能台帳を、
役割別ユーザーフローとページ構造へ変換したものとする。
併せて、`PARTICIPANT_ORGANIZER_BEHAVIOR_MODEL_MODERNIZED.md` の
行動実行単位をページ導線へ反映する。

本書の責務は次の4点に限定する。

1. 機能分類（MECE）
2. ページ責務定義（1ページ1主要意思決定）
3. ルーティング定義（最終形と段階公開形の分離）
4. 受入判定の最小要件定義

## 2. Scope and Non-Scope

### Scope

1. 参加者/主催者/運営のUI導線
2. Discover/Entry/Build/Run/Review の段階構造
3. 共有機能 F23/F26/F32 の配置方針
4. 4セグメント行動の実行単位（Trigger/Decide/Act/Verify）

### Non-Scope

1. 画面デザイン詳細（色トークン、コンポーネント設計）
2. API仕様詳細
3. モデル実装詳細

## 3. IA Principles

1. Role First: 参加者と主催者で入口を分離する。
2. Stage First: Discover -> Entry -> Build -> Run -> Review の順で配置する。
3. One Primary Decision per Page: 1ページに主要意思決定は1つだけ置く。
4. Shared Canonical Source: 共有機能は正本ページを1つ定義する。
5. Fail Safe: 不確実性が高い出力は断定表示しない。
6. Emergency First: 緊急導線は全ページから1ステップ以内で到達可能にする。
7. Action First: 各ページ最上段に「次の1アクション」を置く。
8. Mobile First: 一次行動を3タップ以内に完了可能とする。

## 4. Terminology

本書では段階名称を以下に統一する。

1. Discover
2. Entry
3. Build
4. Run
5. Review

補足: 旧表現 `day-of` は本書では `Run` に統一する。

## 5. Function Classification (MECE)

### 5.1 Participant Functions

1. Discover: F1, F9, F10, F11, F12, F13
2. Entry: F2, F3, F14, F15
3. Build: F4, F20
4. Run: F24, F25
5. Review: F28, F30

### 5.2 Organizer Functions

1. Discover: F5
2. Entry: F16, F17, F18
3. Build: F6, F19, F21, F22
4. Run: F7, F27
5. Review: F8, F29, F31

### 5.3 Shared / Platform Functions

1. Shared Timeline: F23
2. Emergency Communication: F26
3. Community Health: F32

注記: F23/F26/F32 は Shared として一次分類し、
Participant/Organizer 側は「参照導線のみ」を持つ。

## 6. Page Blueprint

注記: 従来のP0-P14は維持しつつ、行動実行点を補うためP15以降を追加する。

### P0 Home

1. URL: `/`
2. Primary Decision: 自分の役割（参加者/主催者）を選ぶ
3. Supports: F23 参照リンク, F26 遷移リンク

### P1 Participant Discover

1. URL: `/participant/discover`
2. Primary Decision: 参加候補を選ぶ
3. Supports: F1, F9, F10, F11, F12, F13

### P2 Participant Entry

1. URL: `/participant/entry`
2. Primary Decision: エントリーを完了する
3. Supports: F2, F3, F14, F15

### P3 Participant Build

1. URL: `/participant/build`
2. Primary Decision: 中盤の補完行動を決める
3. Supports: F4, F20, F23(参照)

### P4 Participant Run

1. URL: `/participant/run`
2. Primary Decision: 当日行動を確定する
3. Supports: F24, F25, F26(参照)

### P5 Participant Review

1. URL: `/participant/review`
2. Primary Decision: 次回参加可否を決める
3. Supports: F28, F30

### P6 Organizer Discover-Entry

1. URL: `/organizer/setup`
2. Primary Decision: 募集設計を確定する
3. Supports: F5, F16, F17, F18

### P7 Organizer Build

1. URL: `/organizer/build`
2. Primary Decision: 未成立対策の優先介入を決める
3. Supports: F6, F19, F21, F22, F23(参照)

### P8 Organizer Run

1. URL: `/organizer/run`
2. Primary Decision: 当日運営の対応順を決める
3. Supports: F7, F24(参照), F25(参照), F26(参照), F27

### P9 Organizer Review

1. URL: `/organizer/review`
2. Primary Decision: 次回改善項目を確定する
3. Supports: F8, F29, F31

### P10 Shared Timeline (Canonical)

1. URL: `/timeline`
2. Primary Decision: 全体進捗を確認する
3. Canonical Feature: F23

### P11 Emergency Hub (Canonical)

1. URL: `/emergency`
2. Primary Decision: 当日変更を送信する
3. Canonical Feature: F26

### P12 Community Health

1. URL: `/community/health`
2. Primary Decision: 偏在・疲弊の注意状態を確認する
3. Canonical Feature: F32

### P13 Legal Hub

1. URL: `/legal`
2. Primary Decision: 規約・同意・権利行使情報を確認する
3. Children:
   - `/legal/terms`
   - `/legal/privacy`
   - `/legal/data-rights`

### P14 Pricing / Plan

1. URL: `/pricing`
2. Primary Decision: 利用プランを選択する

### P15 Participant Trust & Fit

1. URL: `/participant/trust-fit`
2. Primary Decision: 初参加でも進めるかを判断する
3. Supports: F11, F13

### P16 Participant Access Planner

1. URL: `/participant/access-planner`
2. Primary Decision: 移動リスクを許容できるか判断する
3. Supports: F10

### P17 Organizer Momentum Monitor

1. URL: `/organizer/momentum`
2. Primary Decision: 初動48時間で介入するかを判断する
3. Supports: F18, F16

### P18 Organizer Rescue Queue

1. URL: `/organizer/rescue`
2. Primary Decision: 未成立救済の実行順を確定する
3. Supports: F19, F21, F22

### P19 Runbook & Recovery

1. URL: `/run/recovery`
2. Primary Decision: 当日変更時の復旧手順を選ぶ
3. Supports: F26, F27, F7

### P20 Retention Hub

1. URL: `/review/retention`
2. Primary Decision: 次回参加/開催の次アクションを決める
3. Supports: F8, F28, F29, F30, F31

## 7. Final Sitemap (Target Architecture)

### 7.1 Core Routes

1. `/`
2. `/participant/discover`
3. `/participant/entry`
4. `/participant/build`
5. `/participant/run`
6. `/participant/review`
7. `/organizer/setup`
8. `/organizer/build`
9. `/organizer/run`
10. `/organizer/review`
11. `/timeline`
12. `/emergency`
13. `/community/health`
14. `/participant/trust-fit`
15. `/participant/access-planner`
16. `/organizer/momentum`
17. `/organizer/rescue`
18. `/run/recovery`
19. `/review/retention`

### 7.2 Governance / Business Routes

1. `/legal`
2. `/legal/terms`
3. `/legal/privacy`
4. `/legal/data-rights`
5. `/pricing`

## 8. Release Profile (Current Phase)

本節は「最終形」と分離した段階公開定義である。

### 8.1 Wave 1 (MVP)

1. `/participant/discover`
2. `/participant/entry`
3. `/organizer/setup`
4. `/organizer/build`
5. `/organizer/run`
6. `/emergency`
7. `/participant/trust-fit`
8. `/run/recovery`

### 8.2 Wave 2

1. `/participant/build`
2. `/participant/run`
3. `/participant/review`
4. `/organizer/review`
5. `/timeline`
6. `/participant/access-planner`
7. `/organizer/momentum`
8. `/organizer/rescue`
9. `/review/retention`

### 8.3 Wave 3

1. `/community/health`
2. `/legal/*`
3. `/pricing`

## 9. Access and Responsibility Boundaries

1. `/timeline` は F23 の正本表示面とする。
2. `/emergency` は F26 の正本入力面とする。
3. `/community/health` は運営向け参照面とし、一般公開は集約情報に限定する。
4. Participant/Organizer ページでの F23/F26 は「要約表示 + 正本ページ遷移」のみ許可する。

## 10. Minimum Acceptance Contract

各ページは以下を必須スロットとして持つ。

1. Beneficiary（受益者）
2. Primary Decision（主要意思決定）
3. Evidence Scope（表示根拠範囲）
4. Uncertainty Note（不確実性文言）
5. Primary Event（主要計測イベント）
6. Success Metric（成功指標）
7. Fallback Route（失敗時遷移）
8. Owner（責任ロール）
9. Next One Action（次に押す1アクション）
10. Mobile Completion Path（3タップ以内の一次行動導線）

## 11. Coverage Check

### 11.1 Functional Coverage

1. F1-F32 の全機能に Primary Page が1つ割り当てられている。
2. Shared機能 F23/F26/F32 は Canonical Page が1つ定義されている。

### 11.2 Operational Coverage

1. 各公開ページに Primary Event と Success Metric が定義されている。
2. 各公開ページに Fallback Route が定義されている。
3. 各公開ページに Owner が定義されている。

### 11.3 Behavior Coverage

1. 4セグメント x 5段階の主要行動に Primary Page が割当済みである。
2. Trigger/Decide/Act/Verify のうち Act と Verify が各段階で実行可能である。
3. 初参加不安解消、初動48時間介入、当日復旧、終了後継続化の4導線が存在する。

### 11.4 Function-to-Action Bridge

1. F1-F32 は少なくとも1つの実行ページに接続される。
2. F23/F26/F32 は canonical page を持ち、役割ページでは参照導線のみを持つ。

## 12. Function to Page Mapping (Action View)

### 12.1 Participant

1. F1, F9, F12 -> `/participant/discover`
2. F10 -> `/participant/access-planner`
3. F11, F13 -> `/participant/trust-fit`
4. F2, F3, F14, F15 -> `/participant/entry`
5. F4, F20 -> `/participant/build`
6. F24, F25 -> `/participant/run`
7. F28, F30 -> `/participant/review`

### 12.2 Organizer

1. F5, F17 -> `/organizer/setup`
2. F16, F18 -> `/organizer/momentum`
3. F6 -> `/organizer/build`
4. F19, F21, F22 -> `/organizer/rescue`
5. F7, F27 -> `/organizer/run`
6. F8, F29, F31 -> `/review/retention` and `/organizer/review`

### 12.3 Shared

1. F23 -> `/timeline`
2. F26 -> `/emergency` and `/run/recovery`
3. F32 -> `/community/health`

## 13. Governance

1. Owner: ProductOps
2. Reviewers: DevOps, DataOps, MLOps, LegalOps, MarketingOps
3. Update Trigger:
   - 機能台帳変更
   - 行動定義変更（`PARTICIPANT_ORGANIZER_BEHAVIOR_MODEL_MODERNIZED.md`）
   - 段階公開方針変更
   - 重大障害の再発防止
4. Update Rule:
   - Final Sitemap と Release Profile を同時更新する
   - Coverage Check を更新してから承認する
