# STATIC_MOCK_EXECUTION_REPORT

## Status

`STATIC_MOCK_IMPROVEMENT_WBS.md` の現時点実行結果を記録する。

## Completed

1. WBS-0.1 Review Scope Lock
   - `static_site/README.md` に対象外ページとroute mappingを記載済み。
2. WBS-0.2 Acceptance Criteria Freeze
   - 全HTMLに「次にやること」を配置済み。
   - 参加者/主催者/共有ページに緊急導線を配置済み。
   - 参加者画面の内部データモデル名を日本語化済み。
3. WBS-1.1 Competitor Modernization Statement
   - Homeで「バンオフ的な曲・パート成立体験をスマホ/締切/機械支援で扱う」と表現済み。
4. WBS-1.2 MVP Review ROI Gate
   - `STATIC_MOCK_USER_REVIEW_PLAN.md` でユーザー確認論点を定義済み。
5. WBS-2.1 User-Facing Terminology Pass
   - 参加者画面の `EventParticipation`, `SongEntry`, `reason_codes`, `notified_at`, `cooldown_until` を除去済み。
6. WBS-2.2 Reassurance Placement
   - 技術審査なし、完璧でなくてよい、推薦辞退安全性、緊急連絡の復旧可能性を常時表示済み。
7. WBS-2.3 Next Action Consistency
   - 全HTMLに「次にやること」あり。
8. WBS-2.4 Microcopy Flow Review
   - 「自信」表現を正本docsから除去済み。
9. WBS-3.1 Static Mock Data Responsibility Labels
   - 会への参加登録、曲への参加登録、保存される内容、現在状態を表示済み。
10. WBS-3.2 Recommendation Audit Display
    - 参加者向け候補理由、Platform向け `run_id` / `rule_version` / `idempotency_key` / exclusion summary を表示済み。
11. WBS-3.3 Deadline State Variants
    - 参加締切後、曲締切後、推薦締切後のblocked画面を追加済み。
12. WBS-4.1 Product Surface Consistency
    - hero / assurance / next action / record-state の主要順序を整備済み。
13. WBS-4.2 Mobile Touch and Tooltip Polish
    - `.help` を44px以上、tap/hover/focus、外側クリック、ESC closeへ対応済み。
14. WBS-4.3 Navigation Role Consistency
    - 参加者bottom navから主催者操作を除去済み。
    - 主催者bottom navをSetup/Dash/Rescue/Run/Emergencyへ変更済み。
15. WBS-5.1 Component Boundary Draft
    - 本レポート下部にコンポーネント境界候補を記録済み。
16. WBS-5.2 Recommendation Engine Boundary
    - ADR-0046とPlatform Gateで、能力評価なし、自動エントリーなし、監査ありを維持済み。
17. WBS-6.1 User Review Event Plan
    - `STATIC_MOCK_USER_REVIEW_PLAN.md` に観測項目を作成済み。
18. WBS-6.2 Funnel Hypothesis
    - `STATIC_MOCK_USER_REVIEW_PLAN.md` にParticipant/Organizer Flowを定義済み。
19. WBS-7.1 Platform SU Authority Boundary
    - Platform SU操作をPlatform画面へ隔離済み。
20. WBS-7.2 Privacy and Public Member Display Review
    - ADR-0046 Open Questionsとして残っている公開範囲/保持期間/本人設定を未決定事項として扱う。
21. WBS-7.3 Consent and Notification Text Review
    - 通知許可、推薦辞退、緊急連絡の意味を画面とレビュー計画に反映済み。
22. WBS-8.1 Static Artifact Validation
    - link/script検査、`git diff --check`、HTTP取得で検証。
23. WBS-8.2 Accessibility and Regression Review
    - 禁止表現、内部用語、tooltip、色非依存表示を検査。
24. WBS-8.3 User Review Readiness Gate
    - 5者レビューのうち残指摘を反映し、ユーザー確認前の主要ブロッカーを解消。
25. WBS-9.1 Role Definition Reuse
    - `web-designops`, `uiux-designops`, `psychologyops` を追加済み。
26. WBS-9.2 Epistemic Audit
    - AIレビュー合意と実ユーザー検証を区別する記述をWBS/レビュー計画に反映済み。

## Post-Render Corrections (2026-07-19)

上記「Completed」は**チェックリスト単位**で判定されており、実際にブラウザで
レンダリングした結果と一部乖離していた。実物レンダリング（SPビューポート375px）で
確認したところ、以下3点は「完了」記載だが未達だったため修正した。教訓として、
完成判定はチェックリストではなくレンダリング結果に対して行う。

1. **ブランドロゴ崩れ（全31ページ）** — `.brand:before` の3色ドット装飾が
   ワードマーク "music" に重なり「●●usic platform」と表示されていた。
   ドットのサイズ/間隔と `margin` を調整し、文字の上部に分離配置。
2. **主催者ボトムナビ未変更（WBS-4.3の記載と乖離）** — `organizer/*.html` は
   `run.html` を除き参加者ナビ（Home/Events/Songs/My/Emergency）のままだった。
   6ページを主催者ナビ（Setup/Dash/Rescue/Run/Emergency）へ差し替え、
   ページ別にactive状態を設定。
3. **内部用語の漏れ（WBS-2.1の記載と乖離）** — `songs/entry.html` のeyebrowに
   内部モデル名 `Confirm SongEntry` が露出。加えて18ページのeyebrowが
   英語の内部ルート名（"Organizer / Run", "Exception Queue" 等）で、
   日本語ユーザーコピーと混在していた。全て日本語のユーザー向け短ラベルへ統一。

### デザインシステム刷新（`assets/styles.css` 全面書き換え）

視線誘導 > 認知負荷低減 > 情報階層（正本UI優先順位）に沿って、minify済みCSSを
可読な展開形へ書き換えつつ以下を導入した。全31ページへ一括適用され、既存クラス名は
全て保持（使用状況を棚卸しの上）。

- **文字ウェイト階層の導入** — 従来ほぼ全要素が900〜950で、見出し(既定700)より
  下位ラベルの方が太いという階層逆転が起きていた。400 body / 500 secondary /
  600 data / 700 label・CTA / 800 heading のスケールへ再設計し、見出しが最も重い
  要素になるよう修正。
- **見出しサイズ縮小** — H1 clamp上限 68→38px（SPで語中改行していたのを解消、
  `overflow-wrap` 追加）、H2 38→25px。
- **情報密度・装飾の適正化** — ヒーロー高さ・影・角丸を抑え、製品らしい密度へ。

## Pending by Dependency

1. WBS-9.3 PDCA After User Review
   - ユーザー確認完了後に `STATIC_MOCK_USER_REVIEW_PLAN.md` のOutput Templateへ記録し、次回WBSへ反映する。

## Component Boundary Draft

| Component | Responsibility | Static source |
| --- | --- | --- |
| `NextAction` | 次の1行動とPrimary CTA | `.next-action` |
| `RecordPanel` | 保存/監査/責務として残る情報 | `.record-panel` |
| `StatePanel` | 現在状態、締切、blocked状態 | `.state-panel` |
| `Assurance` | 心理的に重要な常時安心材料 | `.assurance` |
| `HelpTooltip` | 補足説明のtap/hover/focus表示 | `.help`, `.help-tip`, `app.js` |
| `SlotRow` | 曲スロットの充足/空き表示 | `.slot-row`, `.slot-mark` |
| `BottomNav` | ロール別主要導線 | `.bottom-nav` |

## Verification Commands

```bash
python3 -m http.server 8787 --directory businesses/music_platform/platform/mockups/static_site
```

```bash
git diff --check -- businesses/music_platform platform/adr/ADR-0046-music-platform-participation-and-automated-formation-support.md .claude/agents
```
