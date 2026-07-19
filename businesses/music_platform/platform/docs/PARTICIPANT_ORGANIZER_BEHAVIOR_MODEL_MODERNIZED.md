# PARTICIPANT_ORGANIZER_BEHAVIOR_MODEL_MODERNIZED

## 1. Purpose

本書は、参加者/主催者の想定ユーザー行動を実行単位で定義し、
機能設計と情報設計の不足を検出するための正本である。

`USER_VALUE_ANALYTICS_CANON.md` の4セグメント定義を継承しつつ、
「バンオフ、やろう」由来で有効だった行動設計を再利用し、
モダン運用に必要な要件を追加する。

## 2. Baseline and Modernization Policy

### 2.1 Keep (Bandoff Legacy Strength)

1. イベント単位での成立/未成立の可視性
2. 参加パートの空き状況を前提にした意思決定
3. 当日までの進捗変化を追える運営目線
4. 実運営で使える最低限の速度と単純さ

### 2.2 Upgrade (Modernization)

1. モバイル前提の即断導線（3タップ以内で一次行動）
2. 不確実性と根拠の同時表示（断定回避）
3. 初参加不安に対する行動補助UIの標準化
4. 緊急変更時の影響伝播と復旧導線の短縮
5. 継続率改善のための終了後ナッジ運用

## 3. Persona and Segment Definition

1. Participant Beginner（参加者-初心者）
2. Participant Repeater（参加者-リピーター）
3. Organizer Beginner（主催者-初心者）
4. Organizer Repeater（主催者-リピーター）

### 3.1 Role Relationship (ADR-0049)

Organizer の2セグメントは Participant の対応セグメントの**スーパーセット**である。
主催者は参加者の全権利（会の探索・参加登録・曲エントリー・演奏・自分の担当管理・
緊急連絡）を保持したまま、主催者固有の権利（会の設定・成立形成の俯瞰・例外処理・
当日運営・最終運営責任）を追加で負う。主催者は演奏参加できる。

以降 §4 の "Organizer Beginner" / "Organizer Repeater" 各段階の記述は、**主催者固有の
追加行動のみ**を示す。主催者は同時に対応する Participant セグメントの行動（Discover/
Entry/Build/Run/Reviewの各項）も並行して行う前提であり、これは省略せず両方読むこと。
情報設計への含意は `SITEMAP.md` §3 原則1・§9 境界を参照：主催者面は参加者面への加算
であり、置き換えではない。

## 4. Behavior Decomposition by Stage

本節は、各段階を「行動トリガー -> 判断 -> 実行 -> 確認」に分解する。

### 4.1 Discover

#### Participant Beginner (Discover)

1. Trigger: 参加意欲はあるが失敗不安が高い
2. Decide: 行けるイベントか、怖くないかを判定する
3. Act: 候補を最大3件まで絞る
4. Verify: 主催者信頼シグナルと初参加ハードルを確認する

#### Participant Repeater (Discover)

1. Trigger: 参加先を効率よく選びたい
2. Decide: 相性と移動コストで候補を比較する
3. Act: 条件一致イベントを短時間で選別する
4. Verify: 当日負荷が過密にならないか確認する

#### Organizer Beginner (Discover)

1. Trigger: 開催意図はあるが設計経験が少ない
2. Decide: 開催規模と募集難易度を決める
3. Act: 募集条件の骨子を作る
4. Verify: 抜け漏れチェックで最低導線を満たす

#### Organizer Repeater (Discover)

1. Trigger: 再現性を保ちつつ差別化したい
2. Decide: 過去回との差分設計を決める
3. Act: 初動48時間で反応を観測する
4. Verify: 初動停滞の兆候を検知する

### 4.2 Entry

#### Participant Beginner (Entry)

1. Trigger: 候補は決まったが送信が不安
2. Decide: 担当パートと1曲目を確定する
3. Act: 参加締切までにEventParticipationを確定し、必要に応じてSongEntryへ進む
4. Verify: 参加登録状態、曲別エントリー状態、各締切を確認する

#### Participant Repeater (Entry)

1. Trigger: 複数候補の同時調整が必要
2. Decide: 複数曲の担当バランスを決める
3. Act: エントリーを順次確定する
4. Verify: 過負荷アラートを確認する

#### Organizer Beginner (Entry)

1. Trigger: 募集開始後の不安が高い
2. Decide: 伝わる募集文と導線に修正する
3. Act: 必要情報を補完し公開する
4. Verify: 問い合わせ往復が過剰でないか確認する

#### Organizer Repeater (Entry)

1. Trigger: 初動反応の速度差が出る
2. Decide: 早期介入の要否を判定する
3. Act: 文面ABと告知再配分を実施する
4. Verify: 初回反応率の回復を確認する

### 4.3 Build

#### Participant Beginner (Build)

1. Trigger: 未成立曲が目立ち始める
2. Decide: どこに貢献できるかを判断する
3. Act: 推薦根拠、既存メンバー、自分の負荷を見て補完参加を承諾または辞退する
4. Verify: 自分の負荷が上振れしないか確認する

#### Participant Repeater (Build)

1. Trigger: 自動成立支援の推薦通知が増える
2. Decide: 補完優先度を決める
3. Act: 追加参加、辞退、通知停止、役割調整を選ぶ
4. Verify: 当日進行に破綻がないか確認する

#### Organizer Beginner (Build)

1. Trigger: 未成立曲の停滞が発生する
2. Decide: 機械推薦で処理する通常案件と主催者例外対応を分ける
3. Act: 救済キューの候補、除外理由、通知状況を確認し、例外だけ処理する
4. Verify: 停滞時間の短縮を確認する

#### Organizer Repeater (Build)

1. Trigger: 複数ボトルネックが同時発生する
2. Decide: リスクヒートマップで優先度を確定する
3. Act: 曲別に通知ポリシー、上限、例外プレイブックを適用する
4. Verify: 直前未成立率の推移を確認する

### 4.4 Run

#### Participant Beginner (Run)

1. Trigger: 当日不安が最大化する
2. Decide: まず何をすべきかを判断する
3. Act: 準備チェックリストを消化する
4. Verify: 遅刻/欠席時の連絡手段を確認する

#### Participant Repeater (Run)

1. Trigger: 現場変更が発生する
2. Decide: 演奏集中と運営協力のバランスを決める
3. Act: タイムテーブルに沿って行動する
4. Verify: 緊急連絡ハブで変更を追従する

#### Organizer Beginner (Run)

1. Trigger: 当日障害が断続発生する
2. Decide: 何から復旧するかを決める
3. Act: 優先順アラートに従い対応する
4. Verify: 影響範囲が収束したか確認する

#### Organizer Repeater (Run)

1. Trigger: 直前欠損の再発リスクがある
2. Decide: 代替案と通知順序を決める
3. Act: 自動通知を起点に復旧対応を回す
4. Verify: 進行遅延を最小化できたか確認する

### 4.5 Review

#### Participant Beginner (Review)

1. Trigger: 終了後の記憶が新鮮なうちに評価したい
2. Decide: 次回参加可否を判断する
3. Act: 体験振り返りを記録する
4. Verify: 不安要因が解消可能か確認する

#### Participant Repeater (Review)

1. Trigger: 継続参加の投資対効果を見たい
2. Decide: 次回候補の優先度を決める
3. Act: 次回候補へ行動予約する
4. Verify: スケジュール負荷を再確認する

#### Organizer Beginner (Review)

1. Trigger: 反省点が散在しやすい
2. Decide: 改善対象を1-3件に絞る
3. Act: 改善メモと次回準備タスクを起票する
4. Verify: 次回の実行可能性を確認する

#### Organizer Repeater (Review)

1. Trigger: 改善サイクルを短く保ちたい
2. Decide: テンプレ更新と運営変更の採否を決める
3. Act: ダッシュボード結果をテンプレに反映する
4. Verify: 継続開催率に改善兆候があるか確認する

## 5. Missing Function Pattern (Current Gap)

現行SITEMAPで不足しやすいのは、次の行動パターンである。

1. 初参加不安の解消導線が1ページに凝縮されていない
2. 主催初動48時間の監視/介入導線が弱い
3. 当日変更時の「影響確認 -> 代替実行」導線が分断されやすい
4. 終了後の再参加/再開催ナッジが弱い
5. 参加登録時の参加可能パートと曲別SongEntryが混同されやすい
6. 主催者の通常声かけと機械推薦の責任境界が曖昧になりやすい
7. 参加締切が曖昧だと、当日飛び入り参加を許す誤解が生まれる

## 6. Modern UX Requirements (Actionable)

### 6.1 Decision Speed

1. 各主要ページで「次に押す1アクション」を最上段に配置
2. モバイルで3タップ以内に一次行動（連絡/エントリー/連絡変更）へ到達

### 6.2 Trust and Transparency

1. 推奨表示には根拠と不確実性を常時併記
2. 「断定ではない」ことをUI言語で明示
3. 演奏技術、上手さ、曲品質を推薦条件や参加資格として扱わない
4. 推薦は本人承諾なしに曲エントリーへ変換しない
5. dry_runと推薦通知エンジンの実行切替はPlatform Super User権限であり、主催者UIには置かない
6. 演奏参加は参加締切までに確定した事前登録者に限定し、飛び入り参加導線を置かない

### 6.3 Recovery First

1. 当日障害時は通常導線より緊急導線を優先表示
2. 連絡後に「誰へ何が影響したか」を即時確認可能にする

### 6.4 Retention Loop

1. 参加者: 終了後24時間以内に次回候補を提示
2. 主催者: 終了後72時間以内に改善メモ起票を促す

## 7. Mapping Contract to Sitemap

SITEMAP更新時は次を満たす。

1. 4セグメント x 5段階の主要行動が、少なくとも1つのPrimary Pageを持つ
2. F1-F32の各機能が、行動実行点に接続される
3. Shared機能（F23/F26/F32）は独立ページを持ち、役割ページは参照導線のみ保持する
4. Discover/Entry/Build/Run/Reviewの各段階で、失敗時Fallback Routeを定義する

## 8. Review Rule

1. 本書変更時は `SITEMAP.md` のCoverage Checkを同時更新する
2. 行動定義を変更した場合は `USER_VALUE_ANALYTICS_CANON.md` と矛盾がないことを確認する
