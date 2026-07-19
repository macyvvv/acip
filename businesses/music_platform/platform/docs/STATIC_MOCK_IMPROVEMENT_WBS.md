# STATIC_MOCK_IMPROVEMENT_WBS

## Purpose

`music_platform` の静的プロダクトモックを、ユーザー確認、仕様確定、実装準備へ進めるための
修正WBSとして管理する。

本WBSは `.claude/agents/` の全agent視点を入力にし、直接関係する改善を実行項目へ、
現時点で対象外または将来確認でよいものを Parking Lot へ分離する。

## Current Objective

1. ユーザーが実物のプロダクトとして導線、状態、責務、心理的負荷を確認できる。
2. 静的モックと正本仕様のズレを見える化し、実装前に潰す順序を定義する。
3. `businesses/music_platform/platform/mockups/static_site/` を、次工程のレビュー可能な成果物として安定させる。

## Scope

対象:

- `businesses/music_platform/platform/mockups/static_site/`
- `businesses/music_platform/platform/docs/SITE_PAGE_FLOW.mmd`
- `businesses/music_platform/platform/docs/SITEMAP.md`
- `businesses/music_platform/platform/docs/PARTICIPANT_BEHAVIOR_MODEL.md`
- `businesses/music_platform/platform/docs/ORGANIZER_BEHAVIOR_MODEL.md`
- `businesses/music_platform/platform/docs/PARTICIPANT_ORGANIZER_BEHAVIOR_MODEL_MODERNIZED.md`
- `businesses/music_platform/platform/docs/USER_VALUE_ANALYTICS_CANON.md`
- `platform/adr/ADR-0046-music-platform-participation-and-automated-formation-support.md`

対象外:

- API実装
- 認証/認可実装
- 通知エンジン実装
- 永続DB実装
- 本番ルーティング実装
- 外部公開/配信

## Agent Input Summary

| Agent | 改善入力 | WBS反映 |
| --- | --- | --- |
| accessibility-review | 文字サイズ、コントラスト、可読性、tooltipの知覚可能性 | WBS-4, WBS-8 |
| analytics | 計測イベント名、ファネル、推薦/辞退/緊急連絡の観測点 | WBS-6 |
| business-strategy | 「バンオフ、やろう」の近代化価値、参加者/主催者価値の焦点化 | WBS-1 |
| businessops | 事業価値、優先順位、レビュー可能な範囲の確定 | WBS-0 |
| color-coordination | 色が状態/責務を誤読させないか | WBS-4 |
| creativeops | 画面表現、補助説明、音/映像系は今回はParking Lot | WBS-4, Parking Lot |
| dataops | 会参加、曲参加、推薦監査、締切、状態のデータ責務 | WBS-3 |
| devops | 静的配信、リンク検査、差分検査、route mapping | WBS-8 |
| doc-creation | レビュー可能なドキュメント化、README、WBS整備 | WBS-0, WBS-9 |
| epistemicsops | 推測/事実/未確定の分離、AIレビューの過信防止 | WBS-9 |
| finance-analysis | 実装前投資判断、MVP範囲とROI | WBS-1 |
| image-generation | OGP/将来ビジュアル素材はParking Lot | Parking Lot |
| legal-research | 利用規約、プライバシー、通知同意、参加者公開情報 | WBS-7 |
| legalops | 法務確認の責任境界、ユーザー公開前の法務文言 | WBS-7 |
| lighting-design | music_platformモックでは直接対象外 | Parking Lot |
| market-research | 競合比較、バンオフ文脈、参加者/主催者ニーズ | WBS-1 |
| marketing | ファーストビュー、価値訴求、初参加者コピー | WBS-2 |
| marketingops | 流入後ファネル、SEO/共有導線、計測接続 | WBS-6 |
| mlops | 推薦モデル/通知エンジンの運用境界 | WBS-5 |
| modelops | 推薦ロジックを能力評価へ寄せないモデル選定原則 | WBS-5 |
| opsboard | Ops横断の優先順位統合 | WBS-0 |
| pdca | レビュー後の改善ループ | WBS-9 |
| product-management | 要件、受入条件、MVP範囲、対象外範囲 | WBS-0, WBS-2 |
| productops | Product/UX/Engineering/QAの実行順序 | WBS-0 |
| psychologyops | 不安、評価感、辞退安全性、緊急連絡の罪悪感 | WBS-2 |
| quality-assurance | 受入基準、リンク、状態分岐、回帰確認 | WBS-8 |
| scenario-writing | 画面内マイクロコピーの流れ、将来コンテンツ支援 | WBS-2 |
| secops | 権限境界、Platform SU、dry_run、監査、秘密情報 | WBS-7 |
| software-engineering | 静的モックから実装へ進むためのコンポーネント/状態分離 | WBS-5 |
| sound-design | music_platformモックでは直接対象外 | Parking Lot |
| trainerops | 今回の判断とレビュー手順の再利用可能化 | WBS-9 |
| uiux-designops | 次アクション、モバイル、締切ゲート、ロールナビ | WBS-2, WBS-4 |
| ux-research | ユーザーフロー検証、テスト観点、アクセシビリティ | WBS-2, WBS-8 |
| video-generation | 将来デモ動画はParking Lot | Parking Lot |
| visual-effects | music_platformモックでは直接対象外 | Parking Lot |
| visualops | 色/視覚表現の責務整理 | WBS-4 |
| web-designops | プロダクト感、内部用語除去、ページテンプレート統一 | WBS-4 |

## WBS Structure

- WBS-0: Governance and Review Control
- WBS-1: Strategy and Market Fit
- WBS-2: UX, Psychology, and Copy
- WBS-3: Data Responsibility and State Contracts
- WBS-4: Visual Design and Responsive Product Surface
- WBS-5: Implementation Readiness
- WBS-6: Analytics and Learning
- WBS-7: Security, Privacy, Legal, and Authority Boundaries
- WBS-8: QA, DevOps, and Verification
- WBS-9: Knowledge Reuse and PDCA

## WBS-0 Governance and Review Control

### WBS-0.1 Review Scope Lock

- Owner: ProductOps
- Supporting agents: businessops, opsboard, doc-creation
- Input: `STATIC_MOCK_IMPROVEMENT_WBS.md`, `README.md`, `SITEMAP.md`
- Output: ユーザー確認対象、対象外、完了条件の固定
- Dependency: なし
- DoD:
  - 今回モック対象外ページがREADMEに明記されている
  - ユーザー確認で問う論点が「導線/状態/責務/心理負荷」に限定されている

### WBS-0.2 Acceptance Criteria Freeze

- Owner: Product Management
- Supporting agents: quality-assurance, ux-research
- Input: 静的モック19ページ、レビュー結果
- Output: ユーザー確認前の受入条件
- Dependency: WBS-0.1
- DoD:
  - 全ページに「次にやること」がある
  - 緊急導線が参加者/主催者/共有ページから1ステップ以内
  - 参加者画面に内部データモデル名が露出していない

## WBS-1 Strategy and Market Fit

### WBS-1.1 Competitor Modernization Statement

- Owner: Business Strategy
- Supporting agents: market-research, marketing
- Input: 「バンオフ、やろう」近代化方針、ADR-0046
- Output: ファーストビューとREADMEに置く価値仮説
- Dependency: WBS-0.1
- DoD:
  - 「曲・パート成立体験をスマホ/締切/機械支援で近代化する」ことが1文で表現されている
  - 発表会/視聴品質ではなく演奏参加の価値で説明されている

### WBS-1.2 MVP Review ROI Gate

- Owner: BusinessOps
- Supporting agents: finance-analysis, productops
- Input: 19ページモック、対象外ページ一覧
- Output: ユーザー確認で得たい判断と、次に投資する実装範囲
- Dependency: WBS-1.1
- DoD:
  - ユーザー確認で判断する項目が3-5件に絞られている
  - 実装着手前に必要な未決定事項が分離されている

## WBS-2 UX, Psychology, and Copy

### WBS-2.1 User-Facing Terminology Pass

- Owner: Web DesignOps
- Supporting agents: uiux-designops, psychologyops, marketing
- Input: 全HTML
- Output: 参加者/主催者向け日本語ラベル
- Dependency: WBS-0.2
- DoD:
  - 参加者画面に `EventParticipation`, `SongEntry`, `reason_codes`, `notified_at`, `cooldown_until` が出ていない
  - Admin/Platform画面だけ技術・監査用語を許容している

### WBS-2.2 Reassurance Placement

- Owner: PsychologyOps
- Supporting agents: ux-research, marketing
- Input: Event detail, Join, Song Entry, Recommendation, Emergency
- Output: 不安が高い箇所の常時安心表示
- Dependency: WBS-2.1
- DoD:
  - 技術審査なし、完璧でなくてよい、推薦は断ってよい、辞退理由は能力評価に使わない、早い連絡は復旧しやすい、が常時表示されている
  - tooltipは補足に限定されている

### WBS-2.3 Next Action Consistency

- Owner: UIUX DesignOps
- Supporting agents: product-management, quality-assurance
- Input: 全HTML
- Output: 全ページの次アクション統一
- Dependency: WBS-2.1
- DoD:
  - 19ページすべてに「次にやること」ブロックがある
  - Primary CTAは各ページ1つを基本にする
  - Secondary CTAは戻る/詳細/辞退など補助行動に限定されている

### WBS-2.4 Microcopy Flow Review

- Owner: Scenario Writing
- Supporting agents: marketing, psychologyops
- Input: hero, assurance, CTA, tooltip文言
- Output: 画面遷移で文体と温度感が破綻しないコピー
- Dependency: WBS-2.2
- DoD:
  - 「評価される」印象を与える語がない
  - 「遊び/演奏参加/自己判断」の文脈が過不足なく残る

## WBS-3 Data Responsibility and State Contracts

### WBS-3.1 Static Mock Data Responsibility Labels

- Owner: DataOps
- Supporting agents: product-management, software-engineering
- Input: `ADR-0046`, static HTML
- Output: 保存される内容、現在状態、補足説明の分類
- Dependency: WBS-2.1
- DoD:
  - 会への参加登録で参加可能パート、通知可否、担当上限、参加可能日程が見える
  - 曲への参加登録が本人承諾後だけ作られることが見える

### WBS-3.2 Recommendation Audit Display

- Owner: DataOps
- Supporting agents: secops, mlops, modelops
- Input: Recommendation page, Platform Notification Gate
- Output: 参加者向け理由表示とPlatform向け監査表示の分離
- Dependency: WBS-3.1
- DoD:
  - 参加者画面は日本語の候補理由を表示する
  - Platform画面は `run_id`, `rule_version`, `idempotency_key`, exclusion summary を表示する
  - 辞退理由を能力評価へ変換しないことが明示されている

### WBS-3.3 Deadline State Variants

- Owner: DataOps
- Supporting agents: uiux-designops, quality-assurance
- Input: Event closed, Song pages, Recommendation page
- Output: 参加締切/曲締切/推薦締切の状態表示
- Dependency: WBS-3.1
- DoD:
  - 参加締切後fallbackがある
  - 曲締切後と推薦締切後のblocked状態がWBS上の次タスクとして明記される

## WBS-4 Visual Design and Responsive Product Surface

### WBS-4.1 Product Surface Consistency

- Owner: Web DesignOps
- Supporting agents: visualops, color-coordination
- Input: CSS, 全HTML
- Output: プロダクト画面としてのテンプレート統一
- Dependency: WBS-2.3
- DoD:
  - hero -> assurance/notice -> next action -> state/record の優先順が主要ページで揃う
  - 記録/状態/警告/安心表示の色が誤読を生まない

### WBS-4.2 Mobile Touch and Tooltip Polish

- Owner: UIUX DesignOps
- Supporting agents: accessibility-review, quality-assurance
- Input: `.help`, `app.js`, CSS
- Output: tap/hover/focus tooltipの改善
- Dependency: WBS-4.1
- DoD:
  - `.help` のタップ領域が44px以上
  - ESC/外側クリックで閉じる
  - tooltipが主要SP幅で画面外へ出ない

### WBS-4.3 Navigation Role Consistency

- Owner: Web DesignOps
- Supporting agents: uiux-designops
- Input: bottom nav, topbar, emergency link
- Output: 参加者/主催者/Platformのナビ分離
- Dependency: WBS-2.3
- DoD:
  - 参加者bottom navに主催者操作が出ない
  - 主催者bottom navはSetup/Dash/Rescue/Run/Emergency中心
  - Platform画面はPlatform SU領域として区別される

## WBS-5 Implementation Readiness

### WBS-5.1 Component Boundary Draft

- Owner: Software Engineering
- Supporting agents: product-management, dataops
- Input: static HTML/CSS
- Output: 将来実装時のコンポーネント候補
- Dependency: WBS-4.1
- DoD:
  - `NextAction`, `RecordPanel`, `StatePanel`, `Assurance`, `HelpTooltip`, `SlotRow` が候補化されている
  - 静的HTML固有の構造と実装候補が分離されている

### WBS-5.2 Recommendation Engine Boundary

- Owner: MLOps
- Supporting agents: modelops, dataops, secops
- Input: ADR-0046, recommendation screens
- Output: 推薦エンジンとUIの境界
- Dependency: WBS-3.2
- DoD:
  - UIは能力評価を扱わない
  - 推薦は候補理由、除外理由、通知状態を表示できる
  - 自動エントリーは行わない

## WBS-6 Analytics and Learning

### WBS-6.1 User Review Event Plan

- Owner: Analytics
- Supporting agents: marketingops, pdca, productops
- Input: 19ページ導線
- Output: ユーザー確認時の観測項目
- Dependency: WBS-2.3
- DoD:
  - 参加登録理解、曲参加理解、推薦辞退理解、緊急連絡理解を観測できる
  - 数値化しない主観フィードバックも記録形式がある

### WBS-6.2 Funnel Hypothesis

- Owner: MarketingOps
- Supporting agents: marketing, analytics, pdca
- Input: Home -> Events -> Join -> Songs -> Entry -> My
- Output: モック確認後に検証するファネル仮説
- Dependency: WBS-6.1
- DoD:
  - 離脱しやすい地点と理由仮説が明記される
  - 初参加者と主催者で分けて記録できる

## WBS-7 Security, Privacy, Legal, and Authority Boundaries

### WBS-7.1 Platform SU Authority Boundary

- Owner: SecOps
- Supporting agents: devops, dataops
- Input: Platform Notification Gate, organizer pages
- Output: Platform SU限定操作の明示
- Dependency: WBS-3.2
- DoD:
  - `dry_run`, 送信実行, kill switch が主催者画面へ露出していない
  - 主催者は状態確認と例外処理だけを扱う

### WBS-7.2 Privacy and Public Member Display Review

- Owner: LegalOps
- Supporting agents: legal-research, dataops
- Input: song detail, member public activity, ADR open questions
- Output: 担当者名/参加履歴表示の未決定事項リスト
- Dependency: WBS-3.1
- DoD:
  - 公開範囲、保持期間、本人設定が未決定として明示されている
  - ユーザー確認時に法務未確定事項として誤承認されない

### WBS-7.3 Consent and Notification Text Review

- Owner: Legal Research
- Supporting agents: legalops, psychologyops
- Input: notification opt-in, recommendation, emergency
- Output: 通知同意、辞退、緊急連絡の法務/心理境界
- Dependency: WBS-7.2
- DoD:
  - 通知許可の意味が過不足なく説明される
  - 推薦辞退が不利益評価にならないことが明示される

## WBS-8 QA, DevOps, and Verification

### WBS-8.1 Static Artifact Validation

- Owner: DevOps
- Supporting agents: quality-assurance
- Input: static_site
- Output: 検証コマンドと結果
- Dependency: WBS-4.2
- DoD:
  - HTML数が期待通り
  - link/script切れ0
  - `git diff --check` 通過
  - local `http.server` で主要ページ取得成功

### WBS-8.2 Accessibility and Regression Review

- Owner: Quality Assurance
- Supporting agents: ux-research, accessibility-review
- Input: tooltip, CTA, nav, status labels
- Output: ユーザー確認前のQA checklist
- Dependency: WBS-8.1
- DoD:
  - keyboard focusでtooltip確認可能
  - tap targetが44px以上
  - 色だけに依存しない状態表示
  - 禁止表現/内部用語の再混入がない

### WBS-8.3 User Review Readiness Gate

- Owner: ProductOps
- Supporting agents: devops, dataops, web-designops, uiux-designops, psychologyops
- Input: WBS-8.1, WBS-8.2
- Output: ユーザー確認Go/No-Go
- Dependency: WBS-8.2
- DoD:
  - 5者レビューが `Accept` または残課題がユーザー確認後でよいと合意
  - ユーザーへ見せるURL/起動手順が明確

## WBS-9 Knowledge Reuse and PDCA

### WBS-9.1 Role Definition Reuse

- Owner: TrainerOps
- Supporting agents: opsboard
- Input: `.claude/agents/web-designops.md`, `.claude/agents/uiux-designops.md`, `.claude/agents/psychologyops.md`
- Output: 今後使うレビューagent定義
- Dependency: WBS-0.1
- DoD:
  - 3つのagent mdが存在する
  - scope, non-scope, review checklist, output format が揃っている

### WBS-9.2 Epistemic Audit

- Owner: EpistemicsOps
- Supporting agents: dataops, market-research, legalops
- Input: 各agentレビュー、WBS、仕様文書
- Output: 事実/推測/未決定の分離
- Dependency: WBS-8.3
- DoD:
  - 「レビューで合意した」ことと「実ユーザーで検証した」ことを混同していない
  - 競合/法務/心理に関する未検証断定がない

### WBS-9.3 PDCA After User Review

- Owner: PDCA
- Supporting agents: analytics, marketingops, productops
- Input: ユーザー確認メモ、観測項目
- Output: 次の修正計画
- Dependency: ユーザー確認完了
- DoD:
  - Keep/Change/Park が分類される
  - 次回WBS差分が作成される

## Parking Lot

以下は `.claude/agents` 全体の入力として確認したが、今回の静的モック修正WBSでは直接実行しない。

1. Image Generation / Video Generation
   - OGP、紹介動画、デモ動画の制作はユーザー導線確認後に扱う。
2. Sound Design
   - 音声通知/効果音は現モック対象外。通知体験を作る段階で再検討する。
3. Lighting Design / Visual Effects / Color Coordination for somia
   - somiaコンテンツ特化の役割。music_platformのWeb UIには直接適用しない。
4. Accessibility Review for somia video content
   - 本モックのUIアクセシビリティは `ux-research` / `quality-assurance` / `uiux-designops` で扱う。
5. ModelOps vendor/model selection
   - 推薦ロジックの実装段階までは具体モデル選定しない。

## Executed Immediate Fixes

1. `.help` のタップ領域を44px以上へ拡大した。
2. 曲締切後、推薦締切後のblocked画面を追加した。
3. Platform画面には、緊急連絡は対象イベント画面から行う旨を明示した。
4. `SITEMAP.md` に静的mock URL対応は `static_site/README.md` を正本とする逆参照を追加した。
5. ユーザー確認メモ用テンプレートを `STATIC_MOCK_USER_REVIEW_PLAN.md` に追加した。

## Remaining Post-Review Queue

ユーザー確認後に扱う。

1. ユーザー確認結果を `STATIC_MOCK_USER_REVIEW_PLAN.md` の Output Template へ記録する。
2. Keep / Change / Park を分類し、WBS-9.3として次回WBS差分を作成する。
3. 法務/プライバシー未決定事項を、実装着手前にADRまたはLegal Hubへ昇格する。
