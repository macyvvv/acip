# CF/GB Relative System — Outcome Backlog（旧WBS v3.0）

> 本書はOutcome・Gate・責任分担の参照資料であり、実行WBSではない。実行正本は`WBS.md`と`task_manifest.yaml`。タスク量ではなく、実行command・schema・trigger・自動handoffが不足していたため、2026-07-17に正本から降格した。

| Metadata | Value |
|---|---|
| Version | 3.0 |
| Status | Approved scope / execution not started |
| Strategy SSOT | `Business Strategy.md` |
| WBS owner | PM / Human accountable |
| Last reviewed | 2026-07-17 |
| Next review | Gate 1 decision or 2026-08-03の早い方 |

## 1. 文書目的

`Business Strategy.md` のPhase 1を、検証可能かつ低固定費で実行するための作業計画へ変換する。
対象期間は2026-07-20を起点とする短期0〜3か月、中期3〜12か月とする。

このWBSは事業戦略を変更しない。未確定の戦略事項は仮定で埋めず、意思決定ゲートとして管理する。

## 2. Current Objective

最初の対象エリアで、合法・再現可能なデータ取得と更新を成立させ、ユーザーに独自価値を提供する検索面を公開し、SEO流入から計測可能なアフィリエイト収益までの最小ループを検証する。

### 2.1 実行・証跡規約

- `Owner`は実行責任ロール、`Human`は承認・資本配分の最終責任者を表す。複数Ownerでは先頭をAccountable、後続をResponsibleとする。
- 各タスクは開始時に担当者、状態、期限を割り当て、成果物・根拠・レビュー記録を `businesses/cf_gb_relative_system/artifacts/<task-id>/` に保存する。個人情報や秘密値は保存しない。
- Gate判断は `artifacts/gates/gate-<n>.md` に判定、判定者、日時、参照証跡、例外、失効・再確認日を記録する。証跡リンクのないGateは通過扱いにしない。
- 外部の数値・商品・規約は、一次ソースURL、確認日、snapshot、自己申告か否かをfact sheetに記録する。推測と事実を混在させない。
- `dry_run`、空データ、取得失敗は実績の証拠に使わない。計測実装自体の試験には使えるが、事業・品質Gateの達成には実データが必要。
- WBS変更時はTask ID、依存関係、Gate、Critical Pathを同時確認し、変更理由を末尾のChange Logへ記録する。

### 2.2 用語

| Term | Meaning |
|---|---|
| North Star Proxy | 戦略上のNorth Star「信頼」を運用計測する代理指標。North Starそのものではない |
| Critical field | 営業状態、所在地、営業時間等、誤りが利用者判断へ重大な影響を与える項目。S-032で確定 |
| Fresh | 項目種別ごとのSLO内に、許諾済み一次ソースまたは承認済み確認手段で検証された状態 |
| Major error | Critical fieldの誤り、誤店舗への結合、閉店店の営業中表示等。S-032で列挙 |
| Qualified visit | bot・内部トラフィック等を除外し、S-005の計測契約を満たす訪問 |
| Independent value | 単なる転載ではなく、鮮度証跡、比較可能性、履歴等の利用者固有価値。S-052で判定可能にする |
| SLO | 測定窓、分母、除外規則、閾値、違反時挙動をS-005/S-032で承認したサービス目標 |

## 3. 精査結果

### 3.1 維持すべき戦略

- North Starを「最も信頼されるデータベース」とした点は、既存検索サイトの模倣を避ける方向として妥当。
- `Data First`、履歴保存、出典追跡、Automation Firstは長期的な競争優位と整合する。
- Phase 1で営業と高機能CMSを行わない判断は、固定費と検証前投資を抑える。
- 営業開始を経過期間ではなくROIで判定する考え方は妥当。

### 3.2 実行前に解消すべき欠落

| 論点 | 現状 | WBSでの扱い |
|---|---|---|
| 初期顧客 | ユーザー像と検索課題が未定義 | JTBD調査と検索意図検証をGate 1に設定 |
| 地理範囲 | 全国を示唆するが初期エリア未定 | 1エリア選定後にのみデータ実装 |
| 競合優位 | 品質・鮮度等の方向だけで測定法がない | KPI定義と競合ベースラインを作成 |
| データ取得 | 取得対象、権利、更新頻度、停止手順が未定 | ソース台帳、法務判定、provenanceを先行 |
| データモデル | 履歴保存方針だけでEntity・制約がない | 最小スキーマと履歴モデルを設計 |
| SEO | 掲載数・index数が中心で独自価値の基準がない | 品質ゲート通過ページのみindex対象 |
| 収益 | アフィリエイトの案件、CV、単価が未検証 | 案件審査とunit economicsをGate 2に設定 |
| KPI | 定義、基準値、目標値、計測周期、責任者がない | KPI dictionaryとダッシュボードを作成 |
| Phase 1終了 | 「十分」「安定」の数値がない | 実測後にGate 4で閾値を承認 |
| 運用 | 訂正、閉店、異議申立て、障害対応が未設計 | Runbook、SLA、kill switchをリリース条件化 |

### 3.3 競合から得られる事実と示唆

2026-07-17時点の各社公式公開情報による。掲載数・PVは各社の自己申告であり、第三者検証値ではない。

| 競合 | 公式公開情報 | 示唆 |
|---|---|---|
| ポケパラ | 年間10億PV以上、会員21万人以上を掲げ、店舗・キャスト・ブログ・イベント・口コミ・求人・有料上位表示を提供 | 機能量と広告在庫で正面競争しない。正確性・履歴・更新速度へ集中する |
| MOESTA+ | 運営10年以上、全国対応、店舗2,795件を掲げ、店舗・キャスト・イベント・割引・レビュー等を提供 | 単なる全国店舗一覧では差別化にならない |
| 全国コンカフェマップ | 店舗1,853件、キャスト1,265件を掲げ、検索・SNS連携・店舗向け有料記事等を提供 | 検索フィルタや掲載課金も既存領域。独自の品質証跡が必要 |
| カフェるん | 全国2,855店、月間120万PVを掲げ、無料掲載、店舗管理、集客と求人を提供 | 無料掲載だけでは店舗獲得優位にならない。更新負荷の低さを実証する必要がある |

競合サイト由来の情報は、その規約・著作権・商用利用条件を確認せず取得・再利用しない。競合を初期データソースとして扱わず、店舗公式サイト、店舗公式SNS、店舗からの提供、許諾済みデータ等を候補とする。

## 4. 実行原則

1. 全国展開より、1エリアでの更新ループ成立を優先する。
2. 店舗数より、検証済み店舗率・鮮度・訂正速度を優先する。
3. 取得可否が未判定のソースを本番パイプラインへ接続しない。
4. 取得値、正規化値、公開値、変更履歴、出典を分離する。
5. 独自価値と品質基準を満たさないページはindexさせない。
6. 自動化にはdry-run、監査ログ、再実行性、kill switch、人間承認境界を持たせる。
7. KPIを改善しない機能は追加しない。

## 5. マイルストーン

| Milestone | 期限 | Outcome | Exit Gate |
|---|---:|---|---|
| M0: 前提確定 | 2週 | 顧客課題、初期エリア、取得候補、収益候補が比較可能 | Gate 1 |
| M1: 実現性確定 | 4週 | 法務・データ・SEO・収益の最小構成が承認可能 | Gate 2 |
| M2: 内部パイロット | 8週 | 50店舗以上で取得・履歴・品質計測が反復可能 | Gate 3 |
| M3: 公開パイロット | 12週 | 1エリアの検索面と計測・訂正運用が稼働 | Gate 4 |
| M4: 再現性確立 | 6か月 | 3か月連続で品質・運用SLOを達成 | Gate 5 |
| M5: Phase 1判定 | 12か月 | 拡張・継続・停止とPhase 2移行可否を実測で判断 | Gate 6 |

## 6. 短期Outcome WBS（0〜3か月）

本節と第7節は管理用Outcome一覧であり、直接実行しない。実行担当・成果物・証跡・Human判断は第8節のCanonical Task Registerを正とする。複合Outcomeはsuffix付き子タスクへ分解する。

### 6.1 WP0 — 戦略基準と計測定義（Week 1〜2）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| S-001 | 主要顧客のJTBD仮説を作る | Strategy | — | 来店前の情報不足、比較行動、失敗条件と反証条件を事前登録 |
| S-002 | ユーザーインタビューを実施 | Market Research | S-001 | 初回10人以上。直近来店時期・初訪/常連・エリアで層化し、テーマ飽和まで追加。募集元、脱落、質問票、同意、匿名化、coding、反証結果を保存 |
| S-003 | 店舗側ヒアリングを実施 | Market Research | S-001 | 初回5店舗以上。規模・更新手段・競合掲載有無で層化し、更新負荷、誤情報、送客計測を確認。募集・同意・保持期限を記録し、営業提案はしない |
| S-004 | 初期エリア候補をスコアリング | Strategy / DataOps | S-002, S-003, S-009, S-010 | 3候補以上を店舗密度、需要、一次ソース実現性、競争、法務リスク、運用コストで比較 |
| S-005 | KPI・計測契約v1を定義 | Analytics | S-001 | 算式、grain、event schema/version、timezone、identity/session、bot/internal filter、dedup key、attribution model/window、収益の発生/承認/取消、late data、欠損、source of truth、provider、fetch時刻、対象期間、`real/dry_run`、ownerを定義 |
| S-006 | 初期エリアを仮承認 | Human | S-002, S-003, S-004, S-005 | 1エリア、選定理由、撤退条件をGate記録へ保存。法務・取得実現性によりGate 2で変更可能 |

### 6.2 WP1 — 競合・法務・データソース監査（Week 1〜4）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| S-010 | 競合ベースラインを採取 | Strategy/Data | — | 店舗数、項目、更新導線、鮮度サンプル、収益機能を同一基準で比較 |
| S-009 | 候補エリアのソース実現性を予備評価 | Market Research / DataOps | S-010 | エリア別に一次ソースの量、権利、鮮度、取得コストを同一protocolで標本確認し、URL・確認日・snapshot・仮定を記録 |
| S-011 | データソース台帳を作る | DataOps | S-006 | source_id、URL/owner、取得方法、規約/robots、許諾根拠version・確認日・失効日、頻度、parser owner、last success、項目、分類/PII、downstream、停止方法を記録。個人アカウントは原則対象外 |
| S-012 | 利用規約・著作権・個人情報・表示上の論点を判定 | Legal/Human | S-011 | ソースごとにAllow / Conditional / Deny。owner、証拠version、地域/用途/保存/表示条件、失効・再確認日を記録。期限切れConditionalは自動Denyとし、robotsを許諾の代替にしない |
| S-013 | 画像・キャスト情報を初期Scopeから分離判定 | Legal/Human | S-012 | 同意、権利、削除要求、センシティブ情報の扱いを決定。未決なら公開対象外 |
| S-014 | 訂正・削除・異議申立てポリシーを定義 | Operations/Legal | S-012 | 受付経路、本人確認、対応期限、監査証跡、緊急非公開条件を明記 |
| S-015 | Risk Register v1を作る | PM | S-010, S-011, S-012, S-013, S-014 | 発生確率、影響、予防、検知、owner、期限、残存リスクを記録 |

### 6.3 WP2 — 収益とunit economics検証（Week 2〜4）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| S-020 | 利用可能なアフィリエイト案件を調査 | Finance/Marketing | S-002 | 審査条件、対象商材、成果条件、単価、広告表示義務、禁止媒体を証跡付きで整理 |
| S-021 | 送客イベントを定義 | Analytics | S-005, S-020 | outbound、予約等の計測可否、click/sub ID、案件report照合、重複排除、承認/取消、attribution、同意、cross-device非対応範囲を定義 |
| S-022 | Phase 1 unit economicsモデルを作る | Finance | S-020, S-021 | 流入×CTR×CVR×単価−変動費。base/upside/downsideを算出 |
| S-023 | 収益成立性を判定 | Human | S-022 | 成立仮説、検証期間、損失上限、停止条件を承認。案件なしでもデータ検証継続可否を明記 |
| S-024 | ポジショニング・メッセージ基準を定義 | Marketing | S-002, S-003, S-010 | audience/channel別に課題、価値命題、根拠、禁止表現、CTA、fact provenance、確認日、self-critiqueを記録。未検証の効果・体験を事実表現しない |

### 6.4 WP3 — データ基盤の最小設計（Week 3〜6）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| S-030 | 最小データ契約を定義 | DataOps / Architecture | S-005, S-012 | Store、Location、Hours、Category、Source、Observation、Changeの型・制約、stable store_id、source identity、alias、移転/閉店、merge/split、項目別source優先度、競合状態を定義。外部値をuntrustedに分類し表示context別escape、URL scheme、server fetch制約を契約化 |
| S-031 | provenance・履歴・再処理モデルを定義 | DataOps / Architecture | S-030 | immutable raw、normalized、publishedを分離。各公開項目からsource locator、observed/source-updated/verified/valid/published time、raw hash、rule/schema/adapter/config version、review/override actor、pipeline commit、artifact IDへ逆引き可能にする。migration、backfill、late arrival、tombstone、任意batch再処理とrollbackを定義 |
| S-032 | 品質ルールを実装可能な形で定義 | DataOps | S-030 | Accuracy、Freshness、Coverage、Consistency、Traceabilityに加え、critical/non-critical分類、項目別SLO、entity match精度、conflict率、stale/未解決時の非公開挙動、標本母数・層・seed・除外・信頼区間を定義 |
| S-033 | 取得アダプタの優先順位を決定 | Architecture | S-011, S-012, S-030 | 許諾済み一次ソースのみを費用、変更耐性、取得頻度で順位付け。原則は決定的処理を優先し、AI候補は非AI baseline、品質差、費用、latency、再現性、外部送信可否を比較してS-038へ送る |
| S-034 | セキュリティ・保持・アクセス設計 | SecOps / DataOps | S-030, S-031 | data inventory、処理目的、PII最小化、human/CI/runtime権限分離、秘密管理、保持・削除検証、backup、監査、vendor transferを定義 |
| S-035 | ADRと実装計画を承認 | Human / Architecture | S-030, S-031, S-032, S-033, S-034 | アーキテクチャ、責任境界、データモデル、代替案、forward/backward migration、互換期間、rollback時データ互換性をADR化。business-agent利用時はinteractive/unattended pathとADR-0039の同期責任を明記 |
| S-036 | Delivery baselineを構築 | DevOps / Engineering | S-035 | dev/preview/prodの設定・データ・権限を分離。dependency lock、秘密値を含まない`.env.example`、deterministic build、schema/fixture/unit/integration/security smokeの必須CI、versioned artifact、SBOM/release manifest、preview、承認付きproduction昇格、rollbackを整備 |
| S-037 | Threat・Privacy modelを承認 | SecOps / Architecture | S-030, S-031, S-034, S-035 | asset、trust boundary、data flow、attacker、abuse caseを記録し、外部入力、XSS/SSRF/悪性URL、訂正受付、analytics、CI/CD、admin、retention/deletion、incident responseのcontrol・試験・残存risk ownerを承認 |
| S-038 | AI/自動判断の採否を記録 | ModelOps / Human | S-035 | defaultは非AI。採用時のみ対象判断、決定的baseline、model/vendor/version、評価set・合格基準、fallback、confidence/abstain、人間承認境界、費用上限、drift/retirement対応を承認。未採用ならN/Aを記録 |

### 6.5 WP4 — 50店舗データパイロット（Week 5〜8）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| S-040 | 取得・正規化・履歴保存を実装 | Engineering / DataOps | S-035, S-036, S-037, S-038（AI採用時） | dry-run、冪等性、retry、rate limit、監査、kill switch、migration/version hookを実装。XSS/HTML/Unicode/悪性URL/redirect/SSRFを防ぎ、AI採用時はmodel/prompt/config、入出力hash、cost、fallback、reviewを監査可能にする |
| S-042 | 自動品質検査fixtureを先行実装 | DataOps / QA | S-032, S-040 | schema、必須、重複、範囲、鮮度、source、entity候補、競合、adversarial caseをfixtureで検査・隔離。人間承認なしの破壊的mergeを禁止し、AI出力は公開へ直結させない |
| S-041 | 50店舗以上のパイロットデータを取得 | DataOps | S-040, S-042 | Deny/期限切れConditionalは取得前block。raw landing後、検疫通過recordだけをnormalized/published候補へ昇格し、全recordのsource、batch、日時、version、checksumを保持 |
| S-043 | 人手による層化サンプル監査 | QA | S-041, S-042 | 店舗数だけでなくsource・項目risk・categoryで層化し、承認済み母数・seed・信頼区間で一次情報と照合。AI採用時はgold sampleで項目別誤りと棄却を検証 |
| S-044 | 差分・障害・再処理を3回反復 | DataOps / DevOps | S-041, S-042 | 3回すべて品質検査まで完了。部分障害、schema変更、late arrivalを注入し、checkpoint再開、任意batch再処理、raw/履歴不変、重複ゼロ、diff/誤検知、復旧ログを確認 |
| S-046 | Gate 3前の復旧・停止演習 | DevOps / DataOps | S-044 | kill switch、backup/restore、rollback、再処理、reconciliation、監査log欠損検知を演習し、暫定RPO/RTO内の復旧証跡と残存riskを保存 |
| S-045 | Data Readiness Review | Human / DataOps | S-043, S-044, S-046 | Gate 3の全条件と証跡をレビュー。不合格なら公開実装へ進まない |

### 6.6 WP5 — 公開パイロット（Week 7〜12）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| S-050 | 検索情報設計とプロトタイプ検証 | Product / UX | S-002, S-024, S-045 | 5人以上のtask test。営業中、料金目安、場所、最終確認日、出典、広告導線を誤認なく理解可能 |
| S-051 | 店舗詳細・エリア検索の最小公開面を実装 | Engineering | S-036, S-037, S-050 | mobile-first、accessibility、error/empty/loading、context別escape、safe link、CSP/security headers、JSON-LD安全serializationを実装 |
| S-052 | index品質・crawlゲートを実装 | MarketingOps / DataOps | S-032, S-051 | source・鮮度・必須項目・独自価値を満たすページだけindex可能。canonical、sitemap、robots、rendered HTML、structured-data test、host bot policy、noindex/削除lifecycleを検証 |
| S-053 | 計測と同意管理を実装 | Analytics / SecOps | S-021, S-051 | Search Console、主要event、outbound、errorを個人情報最小化で計測。campaign/source/medium規約とchannel台帳を定義し、provider、fetch時刻、期間、freshness/completeness、`real/dry_run`、API failureを表示。非必須trackingはdefault deny、撤回可能 |
| S-054 | 訂正・非公開フローを実装 | Operations / SecOps | S-014, S-051 | rate limit/bot対策、request ID、最小情報、添付制限、権限分離、緊急時以外の二者承認、append-only監査を実装し、なりすまし・replay・緊急非公開をE2E確認 |
| S-055 | 公開サービスRunbookと監視を作る | Operations / DevOps | S-040, S-051 | 取得、品質隔離、build/deploy、availability、訂正受付のSLI/alert、owner、通知、抑制、escalationを実装。rollback/restore/停止再開に加え、security incidentの封じ込め、証拠保全、公開停止、operator承認付きcredential対応、通知判断を演習 |
| S-056 | 収益導線を限定導入 | MarketingOps / Product | S-023, S-024, S-053 | 広告表記、規約、計測、根拠付きcopyを確認済みの案件のみ導入。UX guardrailを設定 |
| S-058 | リリース前セキュリティ検証 | SecOps / QA | S-051, S-053, S-054, S-055 | secret/dependency/static scan、公開bundle、external input/URL、CSP/header、form abuse、authz、log redaction、backup access、analytics consent、incident drillを検証。Critical/High未解決ならrelease不可 |
| S-059 | Growth計測・実験準備 | MarketingOps | S-024, S-052, S-053, S-056 | baseline report、channel/campaign taxonomy、provider provenance付きdashboard、仮説・実験台帳、事前登録規約、初回PDCA日程とownerを準備。dry-run/空データを実績扱いしない |
| S-057 | 公開判定と限定リリース | Human | S-052, S-053, S-054, S-055, S-056, S-058, S-059 | Gate 4通過後、CI greenの同一versioned artifactを1エリアへ昇格。production smokeとrollbackを確認 |

## 7. 中期Outcome WBS（3〜12か月）

### 7.1 WP6 — 品質・更新運用の再現性（Month 4〜6）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| M-060 | 週次品質レビューを運用 | DataOps / QA | S-057 | KPI、異常、原因、是正を12週連続記録。欠測週は達成扱いにせず、再開条件と連続期間resetを適用 |
| M-061 | 変更検知と優先再確認を改善 | DataOps | M-060 | 営業時間、URL、閉店等の変更種類別precision/recallを計測。AI採用時はdrift、champion/challenger、rollbackを含める |
| M-062 | 店舗確認チャネルを試験 | Operations | S-054 | 営業ではなく情報確認として20店舗以上へ実施。回答率と工数を計測 |
| M-063 | 半自動更新のROIを検証 | DataOps / Finance | M-060, M-061, M-062 | 1店舗・1更新当たりコスト、例外率、品質差を人手運用と比較。AI採用時は推論費と人手review費を含める |
| M-064 | 3か月SLOレビュー | Human | M-060, M-061, M-062, M-063 | Gate 5判定。未達ならエリア拡張を凍結 |

### 7.2 WP7 — SEOとユーザー価値検証（Month 4〜9）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| M-070 | 検索・行動・計測健全性を分析 | MarketingOps / Analytics | S-057 | query、landing、検索利用、outbound、crawl/index coverage、canonical異常、チャネル別費用・成果・停止理由を月次分析。provider provenanceを保持し、虚栄指標だけで評価しない |
| M-071 | 独自価値テンプレートを改善 | Product / Marketing | M-070 | audience/channel別に変更message、期待行動、鮮度、履歴、検証状態、比較可能性、guardrailを実験台帳へ記録して比較 |
| M-072 | 低品質ページを統合・noindex化 | SEO/Data | M-070 | 価値不足・重複・古いページを月次是正。件数増加を目的にしない |
| M-073 | ユーザー再調査 | Market Research | M-071 | 初回15人以上。S-002のinstrument/segmentationを再利用し、baseline、脱落、構成差、正確性認知、意思決定時間、再訪理由、誤情報影響を比較 |
| M-074 | エリア拡張候補を評価 | Strategy | M-064, M-070, M-071, M-072, M-073 | 現行エリアの成功要因が再現可能な場合のみ2地域目を提案 |
| M-075 | 公開後Growth PDCAを運用 | MarketingOps | S-057, M-070 | 初回は公開7日以内、以後月次でPlan/Do/Check/Actを記録。Checkはprovider・fetch時刻・期間・real/dry-runを明記し、Actをrole、task ID、期限、受入条件付きでMarket Research/Marketing/Productへ戻す。dry-runやcoverage不足時はCheck incompleteとする |

### 7.3 WP8 — 収益検証と投資規律（Month 4〜12）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| M-080 | アフィリエイト月次P/Lを運用 | Finance/Analytics | S-056 | click、CV、承認率、EPC、粗利、データ/運用費を月次確定 |
| M-081 | 導線実験を実施 | Product / MarketingOps | M-075, M-080 | 実験台帳へprimary metric、MDE、期間、母集団、assignment、除外、guardrail、停止・採否規則を事前登録。SRM/計測破損は無効、negative/null/inconclusiveも保存 |
| M-082 | チャネル集中度を監視 | Finance | M-080 | 案件・SEOへの依存度と停止時影響を四半期評価 |
| M-083 | 再投資ルールを適用 | Human / Finance | M-080, M-081, M-082 | 確定粗利の範囲内、損失上限付きでデータ品質・取得自動化へ配分 |
| M-084 | 営業ROI仮説を再計算 | Strategy/Finance | M-062, M-080 | 店舗価値、獲得費、想定LTV、回収月数を実測ベースで算出。営業開始はしない |

### 7.4 WP9 — スケール判定（Month 7〜12）

| ID | Task | Owner | Depends | Deliverable / Definition of Done |
|---|---|---|---|---|
| M-092 | 2地域目の事前セキュリティ・法務差分監査 | SecOps / Legal | M-074承認 | 新source、vendor、analytics、権限、PII、同意、削除、地域差を展開前に確認。Critical/High未解決ならM-090を開始しない |
| M-090 | 2地域目を限定展開 | Product / DataOps | M-074承認, M-092 | 同じデータ契約・Runbookで展開し、追加工数と品質差を計測 |
| M-091 | コスト・性能・継続健全性を最適化 | Engineering / Finance | M-090 | 店舗当たり取得・保存・監視コスト、AI採用時の推論/人手review・lock-in、deploy failure/MTTRを可視化。月次restore test、四半期dependency/secret/権限/rollback auditをSLOを壊さず実施 |
| M-093 | Phase 1実績レビュー | PM / Strategy | M-075, M-080, M-081, M-082, M-083, M-084, M-090, M-091, M-092 | KPI推移、完了/未完PDCA、未解決仮説、学習、未達原因、継続コスト、競合変化を統合 |
| M-094 | 12か月投資判断 | Human | M-093 | Scale / Continue / Pivot / Stopを決定。Phase 2移行は別計画・別承認 |

## 8. Canonical Task Register

### 8.1 実行規約

- この台帳だけを実行キューへ転記する。Outcome表の複合親IDは実行しない。
- 新7 specialist rolesはinteractive-only。unattended registryへ存在しないため、全タスクはinteractive sessionまたはHumanにより明示起動する。
- Artifact列は `businesses/cf_gb_relative_system/artifacts/<Task ID>/` 配下の主成果物。Gateは `artifacts/gates/` 配下に保存する。
- Human欄の`Required`は、そのタスク自体がHuman/counsel判断であることを示す。それ以外のエージェントは判断材料を作るだけで、戦略・法務risk・資本配分・公開riskを承認しない。

Evidence profile:

| Code | Required evidence |
|---|---|
| ER | 一次情報URL/snapshot、確認日、sampling、事実/仮説、反証・限界 |
| EL | authority、jurisdiction、effective/verified date、用途、条件、expiry、不明点 |
| EF | 通貨、税、期間、cash/accrual、入力出典、感度、損益分岐、現金露出、除外費用 |
| EI | requirement/contract trace、変更file/version、unit/integration/negative test、rollback |
| EQ | 独立したexpected/actual、環境・fixture version、境界/失敗/回帰、defect/skip |
| EO | SLI/alert、演習log、RPO/RTO、復旧・停止・escalation、残存risk |
| EP | 参照artifact完全性、9 Ops blocker、例外・期限、Go/Rework/Stop options |
| EH | Human/counsel、日時、対象version、選択、上限/条件、失効・再確認、署名記録 |

### 8.2 Phase 0 — Problem / Area Fit

| ID | Outcome | Executor Agent | Supervising Ops | Human | Depends | Artifact | Evidence |
|---|---|---|---|---|---|---|---|
| S-001 | JTBD仮説と反証条件 | business-strategy | businessops | None | — | `jtbd-hypotheses.md` | ER |
| S-002A | ユーザー調査計画・sampling・同意 | market-research | dataops | None | S-001 | `user-research-plan.md` | ER |
| S-002B | ユーザーinterview・coding | market-research | dataops | None | S-002A | `user-interviews.md` | ER |
| S-002C | JTBD反証・synthesis | business-strategy | businessops | None | S-002B | `jtbd-synthesis.md` | ER |
| S-003A | 店舗調査計画・同意 | market-research | dataops | None | S-001 | `store-research-plan.md` | ER |
| S-003B | 店舗調査・synthesis | market-research | dataops | None | S-003A | `store-findings.md` | ER |
| S-010A | 競合一次証拠採取 | market-research | dataops | None | — | `competitor-facts.md` | ER |
| S-010B | 同一protocol dataset・品質確認 | dataops | dataops | None | S-010A | `competitor-dataset.json` | EQ |
| S-010C | 差別化・代替行動評価 | business-strategy | businessops | None | S-010B | `competitive-baseline.md` | ER |
| S-009A | 候補エリアsource採取 | market-research | dataops | None | S-010A | `area-source-facts.md` | ER |
| S-009B | source実現性・cost scoring | dataops | dataops | None | S-009A | `area-feasibility.md` | ER |
| S-004 | 初期エリア比較案 | business-strategy | businessops | None | S-002C, S-003B, S-009B, S-010C | `area-options.md` | ER |
| S-005 | KPI・計測契約v1 | analytics | marketingops | None | S-001 | `measurement-contract.md` | EI |
| S-007 | Phase 1仮説・非目標・撤退条件 | business-strategy | businessops | None | S-002C, S-003B, S-010C | `strategy-hypothesis-register.md` | ER |
| G-1-PACK | Gate 1証拠統合 | opsboard | opsboard | None | S-004, S-005, S-007 | `gate-1-pack.md` | EP |
| G-1-DEC | Problem/Area Fit判断 | Human | businessops | Required | G-1-PACK | `gate-1.md` | EH |

### 8.3 Phase 1 — Legal / Commercial / Architecture Feasibility

| ID | Outcome | Executor Agent | Supervising Ops | Human | Depends | Artifact | Evidence |
|---|---|---|---|---|---|---|---|
| S-011 | Data source台帳 | dataops | dataops | None | G-1-DEC | `source-register.json` | EI |
| S-012A | Source別一次法務調査 | legal-research | legalops | None | S-011 | `source-legal-evidence.md` | EL |
| S-012B | 法務条件・expiry registry | legalops | legalops | None | S-012A | `legal-source-register.md` | EL |
| S-012C | Source利用risk受容 | Human / counsel | legalops | Required | S-012B | `source-clearance.md` | EH |
| S-013A | 画像・人物情報の権利/privacy調査 | legal-research | legalops | None | S-011 | `people-media-legal.md` | EL |
| S-013B | 初期Scope recommendation | legalops | legalops | None | S-013A | `people-media-scope.md` | EL |
| S-013C | 画像・人物情報Scope判断 | Human / counsel | legalops | Required | S-013B | `people-media-decision.md` | EH |
| S-014A | 訂正・削除法務要件調査 | legal-research | legalops | None | S-012B | `correction-legal-requirements.md` | EL |
| S-014B | 訂正・削除業務policy | product-management | productops | None | S-014A | `correction-policy.md` | EI |
| S-014C | 訂正・削除policy承認 | Human / counsel | legalops | Required | S-014B | `correction-policy-decision.md` | EH |
| S-015 | Cross-domain risk register | product-management | productops | None | S-012B, S-013B, S-014B | `risk-register.md` | EP |
| S-020A | Affiliate候補・媒体適合調査 | marketing | marketingops | None | S-002C | `affiliate-offers.md` | ER |
| S-020B | 案件経済条件fact sheet | finance-analysis | businessops | None | S-020A | `affiliate-inputs.csv` | EF |
| S-020C | 案件terms・広告条件調査 | legal-research | legalops | None | S-020A | `affiliate-legal.md` | EL |
| S-021 | 送客・収益state照合契約 | analytics | marketingops | None | S-005, S-020B | `affiliate-measurement.md` | EI |
| S-022 | Phase 1 unit economics | finance-analysis | businessops | None | S-020B, S-021 | `unit-economics.md` | EF |
| S-023A | 12週pilot予算・工数・cash exposure | finance-analysis | businessops | None | S-022, S-035A | `pilot-budget.md` | EF |
| S-023B | 収益仮説・損失上限判断 | Human | businessops | Required | S-023A | `pilot-capital-decision.md` | EH |
| S-024 | 根拠付きpositioning/message | marketing | marketingops | None | S-002C, S-003B, S-010C, S-020C | `message-brief.md` | ER |
| S-030 | Data contract・entity rules | dataops | dataops | None | S-005, S-012C | `data-contract.md` | EI |
| S-031 | Lineage・履歴・再処理設計 | dataops | dataops | None | S-030 | `lineage-contract.md` | EI |
| S-032 | Data quality/SLO仕様 | dataops | dataops | None | S-030 | `quality-spec.md` | EI |
| S-033 | Adapter優先順位・AI候補評価 | dataops | dataops | None | S-011, S-012C, S-030 | `adapter-options.md` | ER |
| S-034 | Security・保持・access設計 | secops | secops | None | S-030, S-031 | `security-data-design.md` | EI |
| S-035A | Architecture ADR案 | software-engineering | productops | None | S-030, S-031, S-032, S-033, S-034 | `architecture-proposal.md` | EI |
| S-035B | Architecture判断 | Human | productops | Required | S-035A | `architecture-decision.md` | EH |
| S-036A | Delivery baseline | devops | devops | None | S-035B | `delivery-baseline.md` | EO |
| S-036B | Delivery baseline独立受入 | quality-assurance | productops | None | S-036A | `delivery-acceptance.md` | EQ |
| S-037A | Threat/Privacy model・control案 | secops | secops | None | S-030, S-031, S-034, S-035B | `threat-model.md` | EI |
| S-037B | 残存security/privacy risk判断 | Human | secops | Required | S-037A | `security-risk-decision.md` | EH |
| S-038A | AI/自動判断の採否recommendation | modelops | modelops | None | S-033, S-035B | `ai-adoption-assessment.md` | ER |
| S-038B | AI採否・費用上限判断 | Human | modelops | Required | S-038A | `ai-adoption-decision.md` | EH |
| G-2-PACK | Gate 2証拠統合 | opsboard | opsboard | None | S-012C, S-013C, S-014C, S-015, S-022, S-023A, S-035B, S-036B, S-037B, S-038B | `gate-2-pack.md` | EP |
| G-2-DEC | Feasibility・area・budget判断 | Human | businessops | Required | G-2-PACK | `gate-2.md` | EH |

### 8.4 Phase 2 — Data Pilot / Gate 3

| ID | Outcome | Executor Agent | Supervising Ops | Human | Depends | Artifact | Evidence |
|---|---|---|---|---|---|---|---|
| S-042A | Data quality fixture・expected case | dataops | dataops | None | S-032, G-2-DEC | `quality-fixtures/` | EI |
| S-040 | 取得・正規化・履歴pipeline | software-engineering | productops | None | G-2-DEC, S-036B, S-037B, S-038B | `pipeline-implementation.md` | EI |
| S-042B | Fixture/harness独立受入 | quality-assurance | productops | None | S-040, S-042A | `fixture-acceptance.md` | EQ |
| S-041 | 50店舗pilot取得・検疫 | dataops | dataops | None | S-042B | `pilot-ingestion-report.md` | EI |
| S-043 | 層化sample独立監査 | quality-assurance | productops | None | S-041 | `data-audit.md` | EQ |
| S-044 | 差分・障害・再処理反復 | dataops | dataops | None | S-041, S-042B | `reprocessing-report.md` | EO |
| S-046 | 復旧・停止・reconciliation演習 | devops | devops | None | S-044 | `recovery-drill.md` | EO |
| G-3-PACK | Data Readiness証拠統合 | opsboard | opsboard | None | S-043, S-044, S-046, S-012B | `gate-3-pack.md` | EP |
| G-3-DEC | Data Readiness判断 | Human | dataops | Required | G-3-PACK | `gate-3.md` | EH |

### 8.5 Phase 3 — Public Pilot / Gate 4

| ID | Outcome | Executor Agent | Supervising Ops | Human | Depends | Artifact | Evidence |
|---|---|---|---|---|---|---|---|
| S-050A | Search PRD・受入基準 | product-management | productops | None | S-002C, S-024, S-032, G-3-DEC | `search-prd.md` | EI |
| S-050B | UX research plan・screener・同意 | ux-research | productops | None | S-050A | `ux-test-plan.md` | ER |
| S-050C | Annotated flow・prototype | ux-research | productops | None | S-050B | `prototype.md` | EI |
| S-050D | Moderated usability test | ux-research | productops | None | S-050C | `usability-report.md` | ER |
| S-050E | Product requirement signoff | product-management | productops | None | S-050D | `approved-prd.md` | EQ |
| S-051A | Application contract・実装計画 | software-engineering | productops | None | S-050E, S-036B, S-037B | `implementation-plan.md` | EI |
| S-051B | Search/results実装 | software-engineering | productops | None | S-051A | `search-implementation.md` | EI |
| S-051C | Store detail/provenance実装 | software-engineering | productops | None | S-051A | `detail-implementation.md` | EI |
| S-051D | State/a11y/security hardening | software-engineering | productops | None | S-051B, S-051C | `surface-hardening.md` | EI |
| S-051E | Public surface独立受入 | quality-assurance | productops | None | S-051D | `surface-acceptance.md` | EQ |
| S-052 | Index/crawl quality gate | marketingops | marketingops | None | S-032, S-051E | `index-gate-report.md` | EQ |
| S-053A | Event/attribution実装・provider証跡 | analytics | marketingops | None | S-021, S-051E | `analytics-implementation.md` | EI |
| S-053B | Consent/privacy control実装 | software-engineering | productops | None | S-020C, S-037B, S-053A | `consent-controls.md` | EI |
| S-053C | Measurement/consent独立受入 | quality-assurance | productops | None | S-053B | `measurement-acceptance.md` | EQ |
| S-054A | Correction/unpublish workflow実装 | software-engineering | productops | None | S-014C, S-051E | `correction-workflow.md` | EI |
| S-054B | Abuse/authz/security検証 | secops | secops | None | S-054A | `correction-security.md` | EQ |
| S-054C | Correction E2E独立受入 | quality-assurance | productops | None | S-054B | `correction-acceptance.md` | EQ |
| S-055A | Data operations runbook/SLI | dataops | dataops | None | S-040, S-051E | `data-runbook.md` | EO |
| S-055B | Deploy/availability/rollback monitoring | devops | devops | None | S-036B, S-051E | `service-runbook.md` | EO |
| S-055C | Security incident runbook/drill | secops | secops | None | S-037B, S-055B | `security-incident-drill.md` | EO |
| S-055D | Runbook・operability独立受入 | quality-assurance | productops | None | S-055A, S-055B, S-055C | `operability-acceptance.md` | EQ |
| S-056A | Eligible offer・claim clearance pack | marketing | marketingops | None | S-020B, S-020C, S-024 | `offer-clearance-pack.md` | ER |
| S-056B | Placement/UX guardrail仕様 | product-management | productops | None | S-050E, S-053C, S-056A | `affiliate-placement-spec.md` | EI |
| S-056C | Affiliate導線実装 | software-engineering | productops | None | S-056B | `affiliate-implementation.md` | EI |
| S-056D | Commercial/UX独立受入 | quality-assurance | productops | None | S-056C | `affiliate-acceptance.md` | EQ |
| S-058 | Release前security verification | secops | secops | None | S-051E, S-053C, S-054C, S-055D, S-056D | `security-release-report.md` | EQ |
| S-059 | Growth計測・実験readiness | marketingops | marketingops | None | S-052, S-053C, S-056D | `growth-readiness.md` | EP |
| G-4-PACK | Public Pilot証拠統合 | opsboard | opsboard | None | S-052, S-053C, S-054C, S-055D, S-056D, S-058, S-059, S-012B | `gate-4-pack.md` | EP |
| G-4-DEC | 公開risk受容 | Human | opsboard | Required | G-4-PACK | `gate-4.md` | EH |
| S-057A | Production限定昇格 | devops | devops | None | G-4-DEC | `production-promotion.md` | EO |
| S-057B | Production smoke/rollback証跡 | quality-assurance | productops | None | S-057A | `production-acceptance.md` | EQ |

### 8.6 Phase 4–5 — Repeatability / Growth / Revenue

| ID | Outcome | Executor Agent | Supervising Ops | Human | Depends | Artifact | Evidence |
|---|---|---|---|---|---|---|---|
| M-060 | 週次独立品質review | quality-assurance | productops | None | S-057B | `weekly-quality-review.md` | EQ |
| M-061 | 変更検知・優先再確認改善 | dataops | dataops | None | M-060 | `change-detection-report.md` | EI |
| M-062 | 店舗確認業務pilot | product-management | productops | None | S-054C | `store-confirmation-pilot.md` | ER |
| M-063 | 半自動更新ROI | finance-analysis | businessops | None | M-060, M-061, M-062 | `update-roi.md` | EF |
| M-065 | 法務証跡定期再調査 | legal-research | legalops | None | S-012B | `legal-revalidation.md` | EL |
| M-066 | Legal registry更新・期限切れblock | legalops | legalops | None | M-065 | `legal-registry-status.md` | EL |
| G-5-PACK | Repeatability証拠統合 | opsboard | opsboard | None | M-060, M-061, M-062, M-063, M-066 | `gate-5-pack.md` | EP |
| G-5-DEC | Repeatability判断 | Human | opsboard | Required | G-5-PACK | `gate-5.md` | EH |
| M-070 | Search・行動・計測分析 | analytics | marketingops | None | S-057B | `growth-analysis.md` | ER |
| M-071A | 改善実験requirement | product-management | productops | None | M-070, M-073 | `improvement-requirement.md` | EI |
| M-071B | Message/variant制作 | marketing | marketingops | None | M-071A | `variant-copy.md` | ER |
| M-071C | Variant実装 | software-engineering | productops | None | M-071B | `variant-implementation.md` | EI |
| M-071D | Variant独立受入 | quality-assurance | productops | None | M-071C | `variant-acceptance.md` | EQ |
| M-071E | Limited experiment rollout | marketingops | marketingops | None | M-071D | `variant-rollout.md` | EO |
| M-072 | 低品質page統合/noindex | dataops | dataops | None | M-070 | `page-quality-actions.md` | EI |
| M-073 | User value再調査 | market-research | dataops | None | M-070 | `user-value-followup.md` | ER |
| M-075 | Growth PDCA | pdca | marketingops | None | M-070, M-071E | `growth-pdca.md` | EP |
| M-080A | Affiliate ledger取得・state照合 | analytics | marketingops | None | S-056D | `affiliate-ledger.csv` | EI |
| M-080B | 月次finance close/P&L | finance-analysis | businessops | None | M-080A | `affiliate-close.md` | EF |
| M-081A | 実験design事前登録 | analytics | marketingops | None | M-075, M-080B | `experiment-plan.md` | ER |
| M-081B | Assignment/variant実装 | software-engineering | productops | None | M-081A | `experiment-implementation.md` | EI |
| M-081C | Instrumentation独立受入 | quality-assurance | productops | None | M-081B | `experiment-acceptance.md` | EQ |
| M-081D | 結果分析・validity判定 | analytics | marketingops | None | M-081C | `experiment-analysis.md` | ER |
| M-081E | Rollout recommendation | product-management | productops | None | M-081D | `rollout-recommendation.md` | EP |
| M-082 | Channel/program集中risk | finance-analysis | businessops | None | M-080B | `concentration-risk.md` | EF |
| M-083A | 再投資可能額・選択肢 | finance-analysis | businessops | None | M-080B, M-081D, M-082 | `reinvestment-options.md` | EF |
| M-083B | 再投資配分判断 | Human | businessops | Required | M-083A | `reinvestment-decision.md` | EH |
| M-085 | 店舗支払意思調査 | market-research | dataops | None | M-062, M-070 | `store-wtp-study.md` | ER |
| M-086 | WTP・offer viability評価 | business-strategy | businessops | None | M-085 | `offer-viability.md` | ER |
| M-084 | 営業CAC/LTV/payback model | finance-analysis | businessops | None | M-080B, M-086 | `sales-roi-model.md` | EF |
| M-074 | 2地域目strategy評価 | business-strategy | businessops | None | G-5-DEC, M-070, M-073, M-084 | `region-expansion-options.md` | ER |

### 8.7 Phase 6 — Regional Replication / Gate 6

| ID | Outcome | Executor Agent | Supervising Ops | Human | Depends | Artifact | Evidence |
|---|---|---|---|---|---|---|---|
| M-092A | 地域/source一次法務調査 | legal-research | legalops | None | M-074 | `regional-legal-research.md` | EL |
| M-092B | 地域legal condition registry | legalops | legalops | None | M-092A | `regional-legal-register.md` | EL |
| M-092C | 地域security/privacy差分監査 | secops | secops | None | M-074 | `regional-security-audit.md` | EQ |
| M-092D | 地域法務risk受容 | Human / counsel | legalops | Required | M-092B, M-092C | `regional-clearance.md` | EH |
| M-090A | 地域rollout計画・受入基準 | product-management | productops | None | M-074, M-092D | `regional-rollout-plan.md` | EI |
| M-090B | Source onboarding/data run | dataops | dataops | None | M-090A | `regional-data-report.md` | EI |
| M-090C | App/config実装 | software-engineering | productops | None | M-090A, M-090B | `regional-implementation.md` | EI |
| M-090D | 地域展開独立受入 | quality-assurance | productops | None | M-090C | `regional-acceptance.md` | EQ |
| M-090E | 2地域目限定公開判断 | Human | opsboard | Required | M-090D | `regional-release-decision.md` | EH |
| M-090F | 2地域目production昇格 | devops | devops | None | M-090E | `regional-promotion.md` | EO |
| M-091A | App性能・cost engineering | software-engineering | productops | None | M-090F | `performance-report.md` | EI |
| M-091B | Delivery reliability/restore audit | devops | devops | None | M-090F | `delivery-reliability.md` | EO |
| M-091C | Unit cost/lock-in finance検証 | finance-analysis | businessops | None | M-091A, M-091B | `scaled-cost-model.md` | EF |
| M-093A | Phase 1仮説・実績synthesis | business-strategy | businessops | None | M-084, M-090F, M-091C | `phase1-evidence-pack.md` | EP |
| G-6-PACK | Phase 1/2判断証拠統合 | opsboard | opsboard | None | M-093A, M-092D | `gate-6-pack.md` | EP |
| G-6-DEC | Scale/Continue/Pivot/Stop判断 | Human | businessops | Required | G-6-PACK | `gate-6.md` | EH |

### 8.8 Role Coverage

| Role | Assigned in Phase 1 WBS | Boundary |
|---|---|---|
| businessops | strategy/finance supervision | Humanの戦略・資本判断を代行しない |
| business-strategy | 仮説、差別化、地域、Phase evidence | 最終戦略判断をしない |
| finance-analysis | unit economics、budget、P&L、ROI | 支出・配分を承認しない |
| productops | requirement→UX→engineering→QA | deploy・横断release判断をしない |
| product-management | PRD、業務flow、acceptance、recommendation | material scopeを変更しない |
| ux-research | prototype/usability | 市場需要の証明に流用しない |
| software-engineering | application/pipeline実装 | delivery・releaseを承認しない |
| quality-assurance | 独立product acceptance | DataOps/SecOps/DevOps gateを代替しない |
| legalops | legal evidence/condition/expiry管理 | legal clearanceを出さない |
| legal-research | primary legal/policy research | 法的助言・最終判断をしない |
| dataops | data contract/pipeline/data quality | product acceptanceを代替しない |
| devops | CI/deploy/monitor/recovery | product requirementを所有しない |
| secops | security/privacy design・verification | Legal clearanceを代替しない |
| marketingops | SEO/measurement/distribution loop | copy・business strategyを所有しない |
| marketing | message/offer/variant copy | 未検証claimを追加しない |
| analytics | measurement/ledger/experiment analysis | dry-runを実績扱いしない |
| pdca | evidence-based improvement loop | 実データなしにCheck完了としない |
| modelops | AI採否評価 | AI導入を自己承認しない |
| opsboard | 9 Ops evidence synthesis | 専門work・Human判断を代行しない |
| mlops | Phase 1 assignedなし | approved media pipeline時のみ |
| scenario-writing | Phase 1 assignedなし | approved narrative/media strategy時のみ |
| image-generation | Phase 1 assignedなし | approved media task時のみ |
| video-generation | Phase 1 assignedなし | approved media task時のみ |
| doc-creation | Phase 1 assignedなし | sourced external documentが具体化した時のみ |
| market-research | market/user/store/WTP調査 | legal/UX acceptanceを代替しない |

## 9. Decision Gates

各Gateは第8節の `G-n-PACK → G-n-DEC` だけで通過する。以下はHuman判断基準であり、Outcome親IDの完了だけでは通過しない。

### Gate 1 — Problem / Area Fit（Week 2）

Go条件:

- 初回ユーザー10人以上、店舗5店以上を層化調査し、募集・脱落・同意・反証結果が記録されている。
- 複数segmentで反復する課題、具体的な失敗、現行代替行動の証拠がある。
- 初期エリアが定量比較で選定されている。
- KPIの定義・取得手段・ownerが決まっている。

未達時: 対象課題またはエリアを再調査し、実装へ進まない。

### Gate 2 — Feasibility（Week 4）

Go条件:

- 50店舗以上を構成できる独立した一次ソース候補がある。
- 全利用ソースがAllowまたは条件充足済みConditionalである。
- 禁止ソースを使わずデータ価値を作れる。
- アフィリエイト案件の有無とunit economics検証方法が確定している。
- 12週パイロットの費用・工数上限が承認されている。
- 初期エリアが取得権利・source実現性を含めて最終確認されている。

未達時: データ取得方法または収益仮説を再設計。取得権限を推測で補わない。

### Gate 3 — Data Readiness（Week 8）

Go条件（初期暫定値。S-005で確定）:

- 50店舗以上を3回連続で品質検査まで冪等更新できる。
- 層化sampleの公開critical fieldについて、published→normalized→immutable raw→許諾済みsourceを100%逆引きでき、hash整合する。
- 必須項目完全率と非重大項目の正確率はS-005/S-032の項目別暫定閾値を満たし、推定値と信頼区間を併記する。
- 人手監査でmajor errorが0件である。
- entity resolution、未解決conflict、破壊的mergeの検査が承認基準を満たす。
- kill switch、障害注入、backup/restore、rollback、再処理が暫定RPO/RTO内で成功している。
- AI採用時のみ、承認済み評価set、model/config version、fallback、人間承認境界が検証済みである。

未達時: 公開面を作らず、原因別に取得・正規化・品質ルールを是正する。

### Gate 4 — Public Pilot（Week 12）

Go条件:

- index対象ページの品質ゲート通過率100%。
- 主要ユーザータスク成功率80%以上。
- 訂正・緊急非公開・rollbackのE2E試験が成功。
- 重大な法務・セキュリティリスクが未解決でない。
- 監視、Runbook、担当、週次レビュー枠が稼働している。
- CIがgreenで、同一versioned artifactの昇格、production smoke、rollbackが成功している。
- analytics provider、fetch時刻、対象期間、real/dry-runが確認でき、実データ取得または実データ移行条件がGate記録にある。
- 初回Growth PDCAの日程、owner、実験台帳が確定している。

### Gate 5 — Repeatability（Month 6）

Go条件（3か月連続）:

- 公開情報のFreshness SLO達成率95%以上。
- 重大誤情報0件、訂正SLA達成率95%以上。
- 自動更新成功率95%以上。
- 例外処理工数が承認上限内。
- S-005で事前承認したprimary user-value指標とnon-inferiority marginを満たす。

未達時: 新エリア・新機能を凍結し、品質か事業仮説を再評価する。

### Gate 6 — Phase 1 / Phase 2 Decision（Month 12）

Phase 2候補化の必要条件:

- データ品質・運用SLOを6か月継続達成。
- 2地域目でも同じ運用モデルを再現できる。
- アフィリエイト粗利が3か月以上プラスで、営業実験費を自己資金で賄える。
- 店舗側価値と支払意思の調査証拠がある。
- 営業CAC、想定LTV、回収期間の仮説が承認基準内。

閾値の最終値は実測データを基にM-093で提示し、人間が資本配分判断として承認する。

## 10. KPI Dictionary Minimum Set

| Layer | KPI | Definition |
|---|---|---|
| North Star Proxy | Verified Fresh Store Coverage | 対象エリアの営業実態店舗のうち、SLO内に一次ソース確認済みの店舗割合。戦略上の信頼5要素のうち鮮度・品質・網羅率を主に代理し、情報量・更新速度は別指標で補完 |
| Quality | Critical Field Accuracy | 人手監査した重要項目の正解数 / 監査重要項目数 |
| Quality | Freshness SLO | 項目種別ごとの最終確認期限内にある公開値の割合 |
| Quality | Traceability | 公開項目からnormalized、immutable raw observation、許諾済みsource、変換/review履歴へhash整合付きで逆引きできる割合 |
| Growth | Qualified Organic Visit | 非botかつ品質ゲート通過ページへのorganic session |
| Product | Search Task Success | 目的店舗の比較・確認を完了できたtask test参加者割合 |
| Product | Verified Outbound Rate | 店舗公式情報または承認済み案件へのoutbound / qualified visit |
| Revenue | Affiliate Gross Profit | 確定報酬−案件直接費−決済等変動費 |
| Efficiency | Cost per Fresh Store | 当月の取得・確認・例外処理費 / Fresh判定店舗数 |
| Operations | Correction SLA | SLA内に確認・訂正・非公開を完了した申立て割合 |
| Technical | Update Success | 期待した更新jobのうち、品質検査まで成功した割合 |

PV、index数、掲載店舗数は診断指標として保持するが、単独で成功判定に使用しない。

## 11. Critical Path

`顧客課題・エリア/source実現性 → 法務判定 → データ契約/ADR → Delivery/Threat baseline → 品質fixture → 実データ取得 → 人手監査 → 障害・復旧演習 → Data Readiness → 公開面 → Security/Growth readiness → 限定公開 → 3か月運用 → 2地域目事前監査 → 再現 → Phase判定`

次工程を止める主要依存は、法務判定、一次ソース確保、データ品質、訂正運用である。UI、全国ページ生成、店舗CMS、キャスト機能はCritical Pathではない。

## 12. Risk Register Initial View

| Risk | Impact | Early Signal | Mitigation / Stop Rule |
|---|---|---|---|
| 取得規約・著作権違反 | Critical | 規約不明、転載依存、削除要請 | 不明はDeny扱い。許諾か独立一次ソースへ切替 |
| 誤情報による利用者・店舗被害 | High | 重大項目の監査不一致、苦情 | 品質隔離、緊急非公開、訂正SLA、source表示 |
| キャスト等の個人情報侵害 | Critical | 同意不明、退職後残存、画像権利不明 | 初期Scope外。明示同意・削除設計なしでは追加しない |
| SEO依存 | High | organic比率過多、update後急減 | direct/repeat価値を計測。固定費を変動収益以下に制限 |
| scaled content化 | High | 低価値ページ急増、index偏重 | 独自価値ゲート、noindex、統合・削除、手動品質監査 |
| アフィリエイト不成立 | Medium/High | 案件なし、審査落ち、EPC不足 | 4週で判定。データ検証継続と事業停止を分けて判断 |
| 更新運用コスト超過 | High | 例外率・確認時間・店舗単価上昇 | 1エリア固定、コスト上限、手作業増加時は拡張停止 |
| 競合との差別化不足 | High | 再訪・task success・店舗回答率が低い | 機能追加より顧客課題と独自品質証跡を再検証 |
| 外部content/URL injection | Critical | escape違反、異常redirect、private network fetch | untrusted分類、context別escape、scheme/host/IP allowlist、S-058で攻撃test |
| Secret leak / supply-chain侵害 | Critical | scan検知、未知artifact、権限逸脱 | identity分離、pin/SBOM/scan、公開停止、operator承認付き失効・rotation |
| 訂正受付の濫用 | High | spam、なりすまし削除、PII添付 | rate limit、本人確認、二者承認、append-only監査、緊急非公開分離 |
| AI判断の無監査導入 | High | model/version不明、費用増、品質drift | default非AI、S-038承認、評価/fallback/abstain、人間責任、rollback |

## 13. Multi-Agent Critical Review

2026-07-17に旧15役割で初回レビュー後、ADR-0041で不足していた3 Ops・7 specialist rolesを追加した。新10役割が再レビューし、9 Ops対応opsboardが25役割の責任境界と分解を統合した。総合判定は `Improve and Proceed`。戦略・期間・1エリア方針は維持し、複合Outcomeを第8節の実行タスクへ分解した。

| Role | Verdict | Decision / WBS反映 |
|---|---|---|
| opsboard | Improve and Proceed | trusted-data release controlを最優先Critical Pathへ統合 |
| devops | Improve | S-036、S-046、release provenance、復旧順序を採用 |
| dataops | Improve | 検査先行、field lineage、entity resolution、immutable raw/reprocessを採用 |
| mlops | Parking Lot | 生成メディアpipelineは非該当。承認済みmedia施策時のみ再評価 |
| modelops | Improve conditional | S-038を採用。AIを必須化せず、採用時だけ評価・fallback・人間境界を要求 |
| marketingops | Improve | S-052、S-053、S-059、M-075、M-081で計測・実験・PDCAを閉ループ化 |
| secops | Improve | S-037、S-058、外部入力対策、M-092の展開前倒しを採用 |
| market-research | Improve | 調査層化・反証・S-009・エリア選定入力を採用 |
| doc-creation | Improve | metadata、artifact/evidence、Gate decision、用語規約を採用。外部文書制作は非Critical Path |
| marketing | Improve | S-024と根拠・禁止表現・channel別messageを採用 |
| analytics | Improve | S-005/S-053の計測契約、provider provenance、real/dry-run区別を採用 |
| pdca | Improve | M-075でActを担当・期限・受入条件付きtaskへ戻す |
| scenario-writing | Parking Lot | Phase 1に物語生成は不要。別承認のmedia戦略時のみ発火 |
| image-generation | Parking Lot | 正確性への寄与がなく、権利・誤認・費用riskを増やすため不採用 |
| video-generation | Parking Lot | 現Scopeに媒体・KPIがないため不採用 |
| businessops | Improve | Gate証拠packとHuman判断を分離し、strategy/finance traceを追加 |
| business-strategy | Improve | 仮説・差別化・WTP・Phase synthesisを原子化 |
| finance-analysis | Improve | pilot budget、cash exposure、ledger state、資本配分分離を追加 |
| productops | Improve | requirement→UX→implementation→QA handoffを正本化 |
| product-management | Improve | PRD、業務flow、acceptance、rollout recommendationを分離 |
| ux-research | Improve | research plan、prototype、moderated testを分離 |
| software-engineering | Improve | Product実装をDevOpsから分離し、component-level outcomeへ整理 |
| quality-assurance | Improve | 実装者と独立したproduct/delivery acceptanceを追加 |
| legalops | Improve | legal condition/expiry registryとHuman clearance境界を追加 |
| legal-research | Improve | primary legal research→LegalOps→Human/counselの3段階を追加 |

主な競合解決:

- SecOpsとGrowthが同じ`S-058`を提案したため、release blockerであるSecurityを`S-058`、Growth readinessを`S-059`、継続PDCAを`M-075`とした。
- DataOpsのthroughputより検疫を優先し、`S-042 → S-041`の順へ修正した。
- DevOpsの復旧演習を公開前Runbookから分離し、Gate 3前の`S-046`へ移した。
- ModelOpsは条件付き採用、MLOpsと生成メディア役割はParking Lotとし、データpipelineへ責務を転用しない。
- 2地域目展開を監査の契機にせず、`M-092 → M-090`の順にした。

## 14. Parking Lot（本WBS対象外）

- 店舗CMSと有料編集
- キャストプロフィール、ランキング、ブログ
- 会員、ポイント、口コミ
- 求人、予約、CRM
- 全国一括展開
- 公開API、B2Bデータ販売、AI検索向け提供
- 店舗営業の開始
- 生成メディアpipeline、scenario、AI画像・動画。別承認された媒体、権利、予算、KPI、削除運用が揃った場合のみ再評価
- CDP、multi-touch attribution、高度な因果推論、自律最適化、有料広告・大規模SNS運用

Gate 6以前に開始しない。重大な外部環境変化がある場合は別途戦略レビューと承認を行う。

## 15. Sources Reviewed

- [Business Strategy](./Business%20Strategy.md)
- [ポケパラ掲載案内](https://www.pokepara.jp/promotion.html)
- [ポケパラ利用規約](https://www.pokepara.jp/kyushu/agree.html)
- [MOESTA+会社概要・サービス概要](https://moe-sta.com/cafe/company)
- [MOESTA+店舗一覧](https://moe-sta.com/cafe/shops)
- [全国コンカフェマップ](https://con-cafe.jp/)
- [全国コンカフェマップ掲載案内](https://con-cafe.jp/shop-register)
- [全国コンカフェマップ利用規約](https://con-cafe.jp/en/rule)
- [カフェるん店舗掲載案内](https://caferun.jp/regist/lp_customer_1/)
- [Google Search spam policies](https://developers.google.com/search/docs/essentials/spam-policies)

## 16. Definition of Done

本WBS全体は以下を満たした時点で完了とする。

- Gate 1〜6の判断と根拠が記録されている。
- データの取得、履歴、品質、公開、訂正、停止が再現可能である。
- 法務・セキュリティ上の重大な未解決事項がない。
- 品質と運用SLOを満たしたうえで、2地域目への再現性を確認している。
- 12か月の収益、費用、顧客価値、競合変化を基に次の資本配分を判断できる。
- Scale / Continue / Pivot / Stopのいずれかが人間により承認されている。
- 第8節の全実行タスクにExecutor、Supervising Ops、Human境界、Depends、Artifact、Evidence profileがある。
- 複合Outcome親IDを実行キューへ投入していない。
- interactive-only roleをunattended registryで実行していない。

## 17. Change Log

| Version | Date | Change | Decision basis |
|---|---|---|---|
| 1.0 | 2026-07-17 | 短期0〜3か月・中期3〜12か月の初版 | `Business Strategy.md`精査と競合公式情報 |
| 2.0 | 2026-07-17 | 15役割レビューを反映。依存関係、delivery/security/data control、計測、PDCA、条件付きAI governanceを修正 | 6 Ops、8実務エージェント、opsboardの統合判定 `Improve and Proceed` |
| 3.0 | 2026-07-17 | ADR-0041の10役割を追加レビューし、全OutcomeをExecutor/Ops/Human/Artifact/Evidence付き実行タスクへ分解 | 9 Ops、15 specialist agents、opsboardの25役割統合 |
