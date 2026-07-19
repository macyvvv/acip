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

参加モデルは ADR-0046 に従い、会への `EventParticipation` と曲別の `SongEntry` を
分離する。セッション会/演奏会は演奏参加の場であり、参加費は視聴品質への対価ではない。
演奏技術、上手さ、曲品質は参加資格、推薦条件、成立判定、ページ導線の評価軸にしない。
通常の候補抽出と通知は機械が担い、本人承諾なしに曲へ自動エントリーしない。
演奏参加は参加締切までに確定した事前登録者のみを対象とし、飛び入り参加は扱わない。
参加締切は開催日前に置き、曲別エントリー締切、推薦通知締切、Run導線より上位の
ゲートとして扱う。
`dry_run` と推薦通知エンジンの実行切替は Platform Super User 権限であり、主催者向け
通常機能には含めない。

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
4. Run: F7
5. Review: F8, F29, F31

### 5.3 Shared / Platform Functions

1. Shared Timeline: F23
2. Emergency Communication: F26
3. Automated Notification Gate: F27
4. Community Health: F32

注記: F23/F26/F27/F32 は Shared / Platform として一次分類し、
Participant/Organizer 側は「参照導線のみ」を持つ。

## 6. Page Blueprint

注記: 従来のP0-P14は維持しつつ、行動実行点を補うためP15以降を追加する。

### P0 Home

1. URL: `/`
2. Primary Decision: 自分の役割（参加者/主催者）を選ぶ
3. Target Psychological Barrier: どこから始めればよいか迷う不安
4. UX Responsibility: 自分の役割を直感的に選択させる
5. Supports: F23 参照リンク, F26 遷移リンク

### P1 Participant Discover

1. URL: `/participant/discover`
2. Primary Decision: 参加候補を選ぶ
3. Target Psychological Barrier: 自分に合わないイベントを選ぶ不安、初参加で浮くのではないかという不安
4. UX Responsibility: 条件を比較しやすい単位で提示する、初参加者向けの不安を隠さず明示する
5. Supports: F1, F9, F10, F11, F12, F13

### P2 Participant Entry

1. URL: `/participant/entry`
2. Primary Decision: 会への参加登録と最初の曲別エントリーを完了する
3. Target Psychological Barrier: 参加登録と曲別エントリーの違いが分からない不安、自分が参加してよいか過度に技術面で悩む不安
4. UX Responsibility: EventParticipationとSongEntryを分けて提示する、参加可能パート・通知可否・担当上限を登録させる、参加締切を明示する、技術審査ではないことを明示する
5. Supports: F2, F3, F14, F15

### P3 Participant Build

1. URL: `/participant/build`
2. Primary Decision: 中盤の補完行動を決める
3. Target Psychological Barrier: どこまで貢献すべきかの迷い、未成立曲が多いときの焦り
4. UX Responsibility: 優先度を明確にする、補完の判断基準を示す、準備負荷を分散する
5. Supports: F4, F20, F23(参照)

### P4 Participant Run

1. URL: `/participant/run`
2. Primary Decision: 当日行動を確定する
3. Target Psychological Barrier: 当日になってからの不安増大、実際の進行についていけない懸念
4. UX Responsibility: 当日チェックリストを短く提示する、迷ったら次に何をすべきかを示す
5. Supports: F24, F25, F26(参照)

### P5 Participant Review

1. URL: `/participant/review`
2. Primary Decision: 次回参加可否を決める
3. Target Psychological Barrier: 楽しかったが次回も行けるか不安、何を基準に次回を選ぶべきか曖昧な状態
4. UX Responsibility: 振り返りを行動に変換する、継続判断の材料を短くまとめる
5. Supports: F28, F30

### P6 Organizer Discover-Entry

1. URL: `/organizer/setup`
2. Primary Decision: 募集設計を確定する
3. Target Psychological Barrier: どこまで準備すればよいか分からない不安、設計条件が曖昧で決めきれない迷い
4. UX Responsibility: 開催条件を明示する、判断に必要な前提を揃える、参加者が不安にならない設計を作る
5. Supports: F5, F16, F17, F18

### P7 Organizer Build

1. URL: `/organizer/build`
2. Primary Decision: 未成立対策の優先介入を決める
3. Target Psychological Barrier: 未成立が増えると焦りが増す、どこに介入すべきか判断が難しい
4. UX Responsibility: 未成立の優先順位を示す、介入すべき曲を可視化する、停滞を放置しない
5. Supports: F6, F19, F21, F22, F23(参照)

### P8 Organizer Run

1. URL: `/organizer/run`
2. Primary Decision: 当日運営の対応順を決める
3. Target Psychological Barrier: 当日変更が重なると対応が追いつかない焦り、伝達漏れが事故につながる不安
4. UX Responsibility: 緊急連絡の窓口を一本化する、当日判断を迷わせない、集金等の責務を抜けなく実行する
5. Supports: F7, F24(参照), F25(参照), F26(参照), F27(参照)

### P9 Organizer Review

1. URL: `/organizer/review`
2. Primary Decision: 次回改善項目を確定する
3. Target Psychological Barrier: 疲労で振り返りが後回しになりやすい、改善点が多いと次回に落とし込めない
4. UX Responsibility: 改善点を1-3件に絞る、再利用できるテンプレを残す、継続可否を冷静に判断する
5. Supports: F8, F29, F31

### P10 Shared Timeline (Canonical)

1. URL: `/timeline`
2. Primary Decision: 全体進捗を確認する
3. Target Psychological Barrier: 全体の状況が見えないことによる孤立感
4. UX Responsibility: 全参加者が同じ進捗を共有し、不透明性を排除する
5. Canonical Feature: F23

### P11 Emergency Hub (Canonical)

1. URL: `/emergency`
2. Primary Decision: 当日変更を送信する
3. Target Psychological Barrier: 変更連絡を見落とす不安、復旧方法が分からない焦り
4. UX Responsibility: 緊急連絡先をすぐ見つけられるようにする、変更影響を即時に伝える
5. Canonical Feature: F26

### P12 Community Health

1. URL: `/community/health`
2. Primary Decision: 偏在・疲弊の注意状態を確認する
3. Target Psychological Barrier: 人が集まらない、負荷が偏ることへの慢性的不安
4. UX Responsibility: コミュニティの健全性を数値で可視化し、偏在を検知する
5. Canonical Feature: F32

### P13 Platform Notification Gate

1. URL: `/platform/notification-gate`
2. Primary Decision: 推薦通知エンジンの送信可否を確定する
3. Target Psychological Barrier: 誤通知、過通知、二重送信、停止遅れへの運用不安
4. UX Responsibility: dry_run結果、候補、除外理由、通知件数、停止状態をPlatform Super Userに限定して表示する
5. Canonical Feature: F27

### P14 Legal Hub

1. URL: `/legal`
2. Primary Decision: 規約・同意・権利行使情報を確認する
3. Target Psychological Barrier: 権利や個人情報がどう扱われるかの不安
4. UX Responsibility: 規約と同意状態を明瞭にし、後からのトラブルを防ぐ
5. Children:
   - `/legal/terms`
   - `/legal/privacy`
   - `/legal/data-rights`

### P15 Pricing / Plan

1. URL: `/pricing`
2. Primary Decision: 利用プランを選択する
3. Target Psychological Barrier: 費用対効果が見合わない懸念
4. UX Responsibility: プランの価値と費用を比較しやすくする

### P16 Participant Trust & Fit

1. URL: `/participant/trust-fit`
2. Primary Decision: 初参加でも進めるかを判断する
3. Target Psychological Barrier: 参加後に負荷が高すぎるのではという懸念、条件が曖昧で判断できないストレス
4. UX Responsibility: 判断材料に根拠を添える、候補を絞るための優先順位を示す
5. Supports: F11, F13

### P17 Participant Access Planner

1. URL: `/participant/access-planner`
2. Primary Decision: 移動リスクを許容できるか判断する
3. Target Psychological Barrier: 迷ったまま会場に行くことへの緊張
4. UX Responsibility: アクセス方法や物理的ハードルを事前に明確にする
5. Supports: F10

### P18 Organizer Momentum Monitor

1. URL: `/organizer/momentum`
2. Primary Decision: 初動48時間で介入するかを判断する
3. Target Psychological Barrier: 初動が弱いと失敗感が早く来る焦り、募集文が伝わるか分からない不安
4. UX Responsibility: 反応データを見て修正する、募集文のテンプレートを維持する
5. Supports: F18, F16

### P19 Organizer Rescue Queue

1. URL: `/organizer/rescue`
2. Primary Decision: 未成立救済の機械推薦状況と例外対応順を確定する
3. Target Psychological Barrier: 自動推薦が適切に動いているか分からない不安、例外対応と通常運用の境界が曖昧になる負担感
4. UX Responsibility: 候補、除外理由、通知状況を明確にする、主催者が扱う例外だけを分離する、演奏順の仮決定と調整責務を持つ
5. Supports: F19, F21, F22

### P20 Runbook & Recovery

1. URL: `/run/recovery`
2. Primary Decision: 当日変更時の復旧手順を選ぶ
3. Target Psychological Barrier: 優先順を誤ると全体が崩れる緊張、現場で判断し続ける負荷感
4. UX Responsibility: 復旧手順を短く提示する、当日判断の認知負荷を下げる
5. Supports: F26, F27, F7

### P21 Retention Hub

1. URL: `/review/retention`
2. Primary Decision: 次回参加/開催の次アクションを決める
3. Target Psychological Barrier: 負荷が高いと継続開催をためらう、一度うまくいかないと離脱しやすい心理
4. UX Responsibility: KPIや進捗を次回に引き継ぐ、離脱理由を言語化できるようにする
5. Supports: F8, F28, F29, F30, F31

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
14. `/platform/notification-gate`
15. `/participant/trust-fit`
16. `/participant/access-planner`
17. `/organizer/momentum`
18. `/organizer/rescue`
19. `/run/recovery`
20. `/review/retention`

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
2. `/platform/notification-gate`
3. `/legal/*`
4. `/pricing`

## 9. Access and Responsibility Boundaries

1. `/timeline` は F23 の正本表示面とする。
2. `/emergency` は F26 の正本入力面とする。
3. `/community/health` は運営向け参照面とし、一般公開は集約情報に限定する。
4. Participant/Organizer ページでの F23/F26 は「要約表示 + 正本ページ遷移」のみ許可する。
5. `/participant/entry` は EventParticipation と SongEntry の境界を明示し、参加可能パート、成立支援通知可否、担当上限を参加登録時に取得する。参加締切後は演奏参加登録を受け付けず、当日参加導線として再利用しない。
6. `/organizer/rescue` は機械推薦の確認と例外処理に限定し、通常時の個別声かけ業務を主催者責務として復活させない。
7. `dry_run`、推薦通知エンジンの実行切替、全体またはイベント単位の停止判断は Platform Super User 権限であり、主催者ページへ露出しない。
8. 静的モックは `platform/mockups/static_site/README.md` の route mapping を正本とし、`.html` ファイル名は本番URLではなく、Sitemap抽象ルートの検証用ページとして扱う。

## 10. Minimum Acceptance Contract

各ページは以下を必須スロットとして持つ。

1. Beneficiary（受益者）
2. Primary Decision（主要意思決定）
3. Target Psychological Barrier（解消すべき心理障壁）
4. UX Responsibility（行動を促すためのUX責務）
5. Evidence Scope（表示根拠範囲）
6. Uncertainty Note（不確実性文言）
7. Primary Event（主要計測イベント）
8. Success Metric（成功指標）
9. Fallback Route（失敗時遷移）
10. Owner（責任ロール）
11. Next One Action（次に押す1アクション）
12. Mobile Completion Path（3タップ以内の一次行動導線）

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
2. 全ての心理障壁が、いずれかのページの Target Psychological Barrier として網羅されている。
3. Trigger/Decide/Act/Verify のうち Act と Verify が各段階で実行可能である。
4. 初参加不安解消、初動48時間介入、当日復旧、終了後継続化の4導線が存在する。

### 11.4 Function-to-Action Bridge

1. F1-F32 は少なくとも1つの実行ページに接続される。
2. F23/F26/F27/F32 は canonical page を持ち、役割ページでは参照導線のみを持つ。

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
5. F7 -> `/organizer/run`
6. F8, F29, F31 -> `/review/retention` and `/organizer/review`

### 12.3 Shared

1. F23 -> `/timeline`
2. F26 -> `/emergency` and `/run/recovery`
3. F27 -> `/platform/notification-gate`
4. F32 -> `/community/health`

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
