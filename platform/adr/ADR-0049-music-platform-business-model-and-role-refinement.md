# ADR-0049: Music Platform Business Model and Role Refinement

## Status

Accepted by operator approval on 2026-07-19.

本ADRは `ADR-0046`（参加と自動成立支援）を置き換えず、その責任分担と情報設計を
2点で明確化・訂正し、さらに未記載だった収益モデルを追加する。`ADR-0046` 側には
本ADRへの前方参照Amendmentを付す。

## Context

`music_platform` の静的モック（`businesses/music_platform/platform/mockups/static_site`）は
「各ページが自身の責務を理解しているかを確認する」ために作られた責務検証物である。
2026-07-19、6つのinteractive Ops/specialist役割（business-strategy, product-management,
ux-research, marketingops, devops, psychologyops）による責務レビューと、それに続く
オペレーターからの訂正で、正本docに次の欠落・誤りがあることが判明した。

1. **収益モデルが正本のどこにも定義されていない。** `ADR-0046` は参加費を「場代・設備費・
   運営費」とだけ規定し、`USER_VALUE_ANALYTICS_CANON.md` は「広告先行収益」と「売上最大化の
   みを目的にした分析」を非対象とする。しかしプラットフォーム運営者にとっての収益源が
   正本に存在しないため、business-strategy役割は `MVP_IDEA_PRIORITIES.md` の Studio Suggest
   Engine を「中核から注意を奪う別事業」として凍結を推奨した。オペレーターの訂正により
   これは誤りと判明：本事業は利用料課金ではなく**アフィリエイトを唯一の収益源**とする。
   つまり Studio Suggest 等は別事業ではなく収益の中核であり、凍結対象ではない。

2. **主催者と参加者のロール関係が排他的に記述されている。** `ADR-0046` の
   "Human and Machine Responsibilities" は Participant / Organizer / Platform Super User を
   並列の責任集合として列挙し、主催者が参加者の権利を含むことを明示しない。この曖昧さの
   下で、本セッション中の初期作業（主催者ページの bottom-nav を参加者ナビと総入れ替え）が
   行われ、主催者から演奏参加導線（Events/Songs/My）を奪う誤りを生んだ。オペレーターの
   訂正：**主催者は一般参加者の全権利を持ち、加えて特別な権利と責任を負う存在であり、
   演奏にも参加できる。**

3. **参加登録のIAに正本矛盾がある。** `SITE_PAGE_FLOW.mmd` は `EventParticipation`（会への
   参加登録）を独立ページ（Join）に分けるが、`SITEMAP.md` P2 は `/participant/entry` へ
   `EventParticipation` と初回 `SongEntry` を統合する。モック実物は join.html（0秒
   meta-refreshのスタブ）/ entry.html / songs/entry.html の3系統が併存し、どちらの正本にも
   一致していない。product-management役割がこれをIA正本矛盾として明示的にフラグした。

## Decision

### 1. Affiliate-only business model

プラットフォーム運営者の収益源は**アフィリエイトのみ**とする。利用料・購読料・出品料・
掲載料による課金は行わない。参加費（`ADR-0046` の場代・設備費・運営費）はユーザー間の
費用であって運営者の収益ではなく、本決定の対象外である。

アフィリエイト面は、調整ワークフローが自然に生む**高インテントの瞬間**に、役立つ推薦
として提示する。広告先行ではなく、ワークフローを所有した結果として得る文脈依存の推薦で
ある。一次面と担当ページ：

- **スタジオ予約**（`MVP_IDEA_PRIORITIES.md` Studio Suggest Engine）— 主に主催者の会場/
  スタジオ選定（organizer setup）、必要に応じ当日運営。これを一次アフィリエイト面とする。
- **機材・譜面・練習リソース** — 曲の準備（song 詳細 / rehearsal prep pack）。二次面。

アフィリエイト推薦は、成立支援推薦（`ADR-0046` §6-7）と同一のガードレールに従う：

1. 根拠と不確実性を常時併記し、断定しない（`USER_VALUE_ANALYTICS_CANON.md` 準拠）。
2. **収益層は成立・公平性層を汚染しない**：スタジオ等の提携条件が、誰が演奏できるか・
   どの曲が成立するか・推薦順位に影響してはならない。マネタイズ面と成立支援面は分離する。
3. 広告先行にしない：ユーザーの実ニーズをワークフローが顕在化させた文脈でのみ提示する。
4. 提携関係を開示する（具体的な広告表示・法務文言は legalops 所管の Open Question）。

### 2. Organizer is a superset of Participant

ロールモデルを次に確定する。

- 既定として、全ユーザーは **Participant**（参加者）である。
- **Organizer**（主催者）は、ある会について参加者が追加で持つロールであり、**参加者の
  全権利（会の探索・参加登録・曲エントリー・演奏・自分の担当管理・緊急連絡）を保持した
  まま**、主催者固有の権利（会の設定・成立形成の俯瞰・例外処理・当日運営）と、最終運営
  責任を負う。主催者は演奏参加できる。
- **Platform Super User**（プラットフォーム運営者）は会の参加ロールではなく、別軸の運営者
  ロールである。この分離は `ADR-0046` のまま維持する（主催者に推薦通知エンジンの
  dry_run/実行切替/停止を与えない）。

情報設計への含意：参加者面（Home/Events/Songs/My/Emergency の土台シェル）は**全ユーザー
共通の基盤**であり、主催者コンソール（Setup/Dashboard/Rescue/Run）は基盤を置き換えるので
はなく、ロール/モード切替で**加算的に**到達する追加面とする。主催者ページが参加者ナビを
総入れ替えする実装は本決定に反するため訂正する。

`PARTICIPANT_ORGANIZER_BEHAVIOR_MODEL_MODERNIZED.md` の4セグメント（参加者/主催者×初心者/
リピーター）は分析単位としては維持するが、「主催者-」セグメントは参加者能力のスーパー
セットとして定義し直す。

### 3. EventParticipation is its own surface (IA source-of-truth)

`SITE_PAGE_FLOW.mmd` の分離モデルを正本とする：`EventParticipation`（会への参加登録）は
独立した意思決定面を持ち、`SongEntry`（曲別担当）はその後の別行動として別面に置く。
`SITEMAP.md` P2 の統合記述は本決定に合わせて更新する。join のスタブ（0秒 meta-refresh）は
実 `EventParticipation` 面に置き換える。

根拠：参加登録は初参加者にとって最初の心理的コミットメントの壁（不安ピーク）であり、専用面
に値する。加えて Organizer⊇Participant（決定2）の下では参加登録フローは全ユーザー共通の
基盤に属し、`SongEntry` と明確に分離しておく方が語彙の多義（"参加"）による混同を避けられる。

## Boundaries

本ADRが**扱わない**こと：

- 具体的なアフィリエイト提携先、手数料率、広告表示の法務文言、異議申立て導線
  （legalops 所管、`ADR-0046` Open Questions の延長）。
- 事前決済・キャンセルポリシー（`ADR-0046` Open Question のまま）。
- ページ単位の詳細な責務仕様と受入基準（`SITEMAP.md` と behavior model 側で定義する）。
- 静的モックの視覚デザイン品質（本件の対象外）。
- Setlist Optimizer（`MVP_IDEA_PRIORITIES.md`）はアフィリエイト直結でないため優先度は
  据え置き。凍結ではなく順序判断であり、本ADRの決定事項に含めない。

## Consequences

- `ADR-0046` に本ADRへの前方参照Amendmentを追加（責任分担がロールのスーパーセット関係で
  読み替えられること、収益モデルは本ADRが正本であること）。
- 次の正本docを同期する（Required Follow-up）：
  - `businesses/music_platform/platform/docs/SITEMAP.md`（IA：EventParticipation独立、
    Organizer面の加算モデル、アフィリエイト面の追加、ページ責務）
  - `businesses/music_platform/platform/docs/PARTICIPANT_ORGANIZER_BEHAVIOR_MODEL_MODERNIZED.md`
    （Organizer⊇Participant のセグメント再定義）
  - `businesses/music_platform/platform/docs/USER_VALUE_ANALYTICS_CANON.md`
    （収益＝アフィリエイトの事業価値層、収益層と成立/公平性層の分離ガードレール）
  - `businesses/music_platform/platform/docs/PARTICIPANT_BEHAVIOR_MODEL.md` /
    `ORGANIZER_BEHAVIOR_MODEL.md`（ロール関係）
- 静的モックの改修義務：主催者ページの排他ナビを加算的ロール切替へ訂正、join スタブを
  実 EventParticipation 面へ、アフィリエイト面（スタジオ/機材）を responsibility として設置。
- 以後、`music_platform` の収益に触れる設計は「アフィリエイトのみ・成立/公平性層を汚さない・
  広告先行にしない」を満たすこと。

## Rejected Alternatives

- **利用料/購読課金モデル**：オペレーターの事業判断によりアフィリエイト一本とするため却下。
- **Studio Suggest 等の凍結**（business-strategy推奨）：アフィリエイトが唯一の収益源である
  以上、スタジオ推薦は中核であり別事業ではないため却下。
- **主催者と参加者を排他ロールとして扱う**（初期作業の暗黙前提）：主催者は演奏参加でき、
  参加者権利のスーパーセットであるため却下。排他ナビ実装もこれに伴い訂正。
- **`SITEMAP.md` の entry統合モデルを正本にする**：参加登録は独立した不安ピーク面であり、
  "参加"語の多義による EventParticipation/SongEntry 混同を避けるため、分離モデルを採る。
- **ADR-0046を全面改訂する**：受理済みADRを書き換えず、明確化・訂正・追加は新ADR＋前方参照
  Amendmentで行う方が決定履歴の追跡性が高いため、新ADRとした。

## Validation

- `platform/adr/ADR-0046-*.md` に本ADR（0049）への Amendment 参照が存在すること。
- `SITEMAP.md` が (1) EventParticipation を独立面として記述、(2) Organizer面を参加者基盤への
  加算として記述、(3) アフィリエイト面を responsibility として含むこと。
- `USER_VALUE_ANALYTICS_CANON.md` に「収益＝アフィリエイトのみ」「収益層は成立/公平性層を
  汚染しない」が明記されること。
- 静的モックで、主催者が参加者導線（Events/Songs/My）を失っていないこと（排他ナビの解消）。
- モック内のアフィリエイト面が `ADR-0046` §6-7 と同一ガードレール（根拠+不確実性・断定回避）で
  表現されていること。
