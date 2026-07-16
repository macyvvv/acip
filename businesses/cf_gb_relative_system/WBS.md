# CF/GB Relative System — Executable Work Breakdown Structure

## 1. Purpose

本書は、事業Outcomeをオーケストレーターが実行できる状態へ接続するPhase -1の実行正本である。旧v3.0の137項目は[OUTCOME_BACKLOG.md](./OUTCOME_BACKLOG.md)へ降格した。

Canonical machine-readable sourceは[`task_manifest.yaml`](./task_manifest.yaml)。本書とmanifestが矛盾する場合、実行を停止して両方を同期する。

## 2. Definition of an Executable Task

Canonical Taskは以下をすべて持つ。

- versioned inputとinput schema
- 明示trigger
- repositoryに存在するcommand、endpoint、またはinteractive workflow
- 変更対象file
- outputとoutput schema
- deterministic acceptance command
- retry、timeout、failure state
- dependencyとmachine-readable next handoff
- task state (`ready/blocked/running/succeeded/failed/quarantined`)

Pathはmanifestの`path_resolution`に従う。`businesses/`、`platform/`、`.github/`で始まるものはrepository-relative、それ以外はbusiness root-relative。Blocked taskのcommand/schemaは依存taskが生成する将来成果を参照できるが、`ready`へ遷移する時点で実在検査に合格しなければならない。

これを満たさない項目はOutcomeであり、Taskと呼ばない。

## 3. Phase -1 Goal

`cf_gb_relative_system`をregistryへ接続し、manifestの先頭から依存解決・実行・証跡検証・状態遷移できる基盤を構築する。Humanの日常運用はportal、MA、policy engine、exception consoleへ置換し、統計判断を再現可能なdata planeへ接続する。

## 4. Human-free Boundary

通常処理は無人化する。戦略・資本上限はownerがpolicyとして一度設定し、日常のGate判定はpolicy engineが行う。不明・期限切れ・法的資格を要する例外は自動許容せず、`quarantined`で安全停止して外部counsel/owner exceptionへ送る。

詳細は[`HUMAN_REPLACEMENT_MATRIX.md`](./HUMAN_REPLACEMENT_MATRIX.md)。

## 5. Statistical Boundary

調査、品質監査、UX、SEO、Affiliate、実験は[`STATISTICAL_PROTOCOL.md`](./STATISTICAL_PROTOCOL.md)に従う。件数のみでは開始・完了できず、population、sampling frame、estimand、precision/power、missingness、stopping ruleを事前登録する。

## 6. Work Packages

| WP | Outcome | Unlocks |
|---|---|---|
| WP-E1 | Business/runtime登録 | business_idをqueueで受理 |
| WP-E2 | Execution role contracts | 全Executorをruntimeで解決 |
| WP-E3 | Manifest・DAG state | ready taskの自動claim/handoff |
| WP-E4 | Artifact/evidence contracts | 無効証跡による完了を防止 |
| WP-E5 | Policy/Gate engine | 日常Human判断をpolicy化 |
| WP-E6 | Research/consent portal | 調査・UX・WTP回答取得 |
| WP-E7 | MA/participant workflow | 募集・quota・reminder・終了event |
| WP-E8 | Correction/exception console | 訂正・本人確認・異議・counsel例外 |
| WP-E9 | Statistical data plane | KPI・品質・実験の再現可能計算 |
| WP-E10 | Delivery/Ops skeleton | preview/prod・監視・復旧 |

## 7. Executable Task Breakdown

Artifactは`artifacts/<task_id>/`、task stateはmanifest/state storeへ保存する。

Checkboxはmanifest stateの表示用projectionとする。`[x]`は`succeeded`、`[ ]`はそれ以外。checkboxだけを手動更新せず、manifestの状態変更と同時に同期する。

### WP-E1 — Business/runtime登録

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-001A | [x] Registry現状とpath契約を確定 | Strategy, repo registry | `command:run_bootstrap_task.py` / Software Engineering | `artifacts/E-001A/output.json` | registration design | machine validatorでregistry状態/root確認 | — | succeeded |
| E-001B | [x] Business registryへ追加 | E-001A | `interactive_agent:software-engineering` | `platform/system/core/business_registry.py`, tests | registered business | targeted pytest＋`get_business()`成功 | E-001A | succeeded |
| E-001C | [x] Business roots・README作成 | E-001A | `interactive_agent:software-engineering` | business `app/`, `artifacts/`, `schemas/`, `templates/` | canonical roots | root existence test | E-001A | succeeded |

### WP-E2 — Execution role contracts

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-002A | [x] 必要runtime roleを最小選定 | Outcome backlog, ADR-0041 | `interactive_agent:businessops` | `artifacts/E-002A/` | role execution matrix | 全Phase 0 Executor解決、不要role除外 | E-001B | succeeded |
| E-002B | [x] Prompt/output/tool/cost contract設計 | E-002A | `interactive_agent:modelops` | contracts・prompt proposal | role contract pack | SecOps/DataOps review | E-002A | succeeded |
| E-002C | [x] Interactive-only role実装（ADR-0041、無人registryは不変） | E-002B | `interactive_agent:software-engineering` | `.claude/agents/*.md`（10role）, ADR-0041 | interactive-only runtime roles | 全E-002B role解決＋`agent_role_registry.py`が8role seedのまま | E-002B | succeeded |
| E-002D | [x] Pre-approval・spend・tool policy | E-002C | `interactive_agent:secops` | `platform/system/tests/test_execution_pre_approval_policy.py`（cf_gb deny-default証明）、実運用`auto_approval_policy.json`のスキーマ移行修正 | deny-default execution policy | unauthorized fixture denied | E-002C | succeeded |

### WP-E3 — Manifest・DAG state

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-003A | [x] Manifest schemaを正本化 | current manifest/schema | `interactive_agent:software-engineering` | `task_manifest.schema.json` | validated schema | jsonschema validation | — | succeeded |
| E-003B | [x] Phase -1 manifestを正本化 | WBS, schema | `interactive_agent:product-management` | `task_manifest.yaml` | task DAG | duplicate/missing/cycle zero | E-003A | succeeded |
| E-004A | [x] State model・atomic claim設計 | E-003B | `command:run_bootstrap_task.py` / Software Engineering | `artifacts/E-004A/output.json` | transition contract | machine validatorでstate/claim/quarantine確認 | E-003B | succeeded |
| E-004B | [x] DAG ready/claim/complete engine | E-004A | `interactive_agent:software-engineering` | `platform/system/core/task_dag_engine.py`, tests | runnable DAG engine | concurrency/crash/replay tests | E-004A, E-002C | succeeded |
| E-004C | [ ] Retry/backoff/resume/reconcile | E-004B | `interactive_agent:devops` | runner reliability modules/tests | recoverable execution | failure injection test | E-004B | ready |

### WP-E4 — Artifact/evidence contracts

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-005A | [x] Artifact共通envelope schema | evidence profiles | `interactive_agent:dataops` | `schemas/artifact-envelope.json` | provenance schema | invalid hash/version rejected | E-001C | succeeded |
| E-005B | [x] Task-type templates/schema | E-005A, stats contract | `interactive_agent:dataops` | `schemas/`, `templates/` | research/legal/finance/code/QA schemas | fixture validation | E-005A | succeeded |
| E-005C | [ ] Evidence validator・completion hook | E-005B, E-004B | `interactive_agent:software-engineering` | validator/runner/tests | evidence-gated completion | invalid artifact cannot succeed | E-005B, E-004B | ready |

### WP-E5 — Autonomous policy/Gate engine

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-006A | [x] 16 Human判断をpolicy/exceptionへ分類 | Outcome backlog | `command:run_bootstrap_task.py` / BusinessOps | `artifacts/E-006A/output.json` | decision automation matrix | machine validatorでowner/fallback確認 | E-003B | succeeded |
| E-006B | [x] Gate policy schema・fixtures | E-006A | `interactive_agent:businessops` | gate policy schema/fixtures | versioned policies | deterministic Go/Rework/Stop fixtures | E-006A | succeeded |
| E-006C | [x] Legal expiry・deny policy | legal registry contract | `interactive_agent:legalops` | legal policy/fixtures | automatic disable rules | expired/unknown always blocked | E-006A | succeeded |
| E-006D | [x] Spend/security/publish policies | E-006A | `interactive_agent:secops` | policy/fixtures | caps and severity rules | over-cap/Critical denied | E-006A | succeeded |
| E-006E | [ ] Policy evaluation engine | E-006B/C/D | `interactive_agent:software-engineering` | policy engine/tests | machine Gate decision | deterministic fixture results | E-005C, E-006B, E-006C, E-006D | blocked |
| E-006F | [ ] Gate/policy console | E-006E | `interactive_agent:software-engineering` | app Gate surface/tests | policy status・override-free normal path | decision/audit E2E | E-006E, E-009D | blocked |
| E-006G | [ ] Legal evidence/expiry dashboard | E-006C | `interactive_agent:software-engineering` | app legal surface/tests | expiry・disable visibility | expiry alert/disable E2E | E-006C, E-009D | ready |
| E-006H | [ ] Spend/cap dashboard | E-006D | `interactive_agent:software-engineering` | app spend surface/tests | committed/forecast/cap visibility | over-cap block E2E | E-006D, E-009D | ready |

### WP-E6–E8 — Portal・MA・exception workflow

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-007A | [ ] Participant/consent/data requirements | stats/legal/privacy contracts | `interactive_agent:product-management` | portal PRD | approved interaction contract | LegalOps/SecOps/DataOps review | E-006E | blocked |
| E-007B | [ ] Research/UX/WTP portal実装 | E-007A | `interactive_agent:software-engineering` | app routes/storage/tests | public intake portal | accessibility/security/E2E tests | E-007A, E-009A | blocked |
| E-007C | [ ] MA workflow・quota/reminder | E-007A | `interactive_agent:software-engineering` | scheduler/workflow/tests | participant automation | dedup/quota/timeout tests | E-007A, E-004C | blocked |
| E-007D | [ ] Portal/MA独立受入 | E-007B/C | `interactive_agent:quality-assurance` | QA artifact | release acceptance | consent/dropout/nonresponse/a11y tests | E-007B, E-007C | blocked |
| E-007E | [ ] Store verification page | E-007A | `interactive_agent:software-engineering` | app store verification/tests | identity/evidence intake | duplicate/dispute/quarantine E2E | E-007A, E-009A | blocked |
| E-007F | [ ] Instrumented usability page | E-007A | `interactive_agent:software-engineering` | app usability/tests | task/error/assist event intake | protocol/event/a11y E2E | E-007A, E-009A | blocked |
| E-008A | [ ] Correction/exception PRD・policy | legal/security requirements | `interactive_agent:product-management` | exception PRD | workflow contract | SLA/identity/escalation complete | E-006E | blocked |
| E-008B | [ ] Correction/exception console実装 | E-008A | `interactive_agent:software-engineering` | console/routes/tests | normal-case automation | abuse/authz/audit E2E | E-008A, E-009A | blocked |
| E-008C | [ ] Counsel/owner quarantine handoff | E-008B | `interactive_agent:legalops` | exception integration/tests | safe exception queue | unresolved case never auto-approved | E-008B | blocked |

### WP-E9 — Statistical data plane

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-009A | [x] Observation/event/study schema | statistical protocol | `interactive_agent:analytics` | data schemas | versioned measurement contract | schema fixtures valid | E-001C | succeeded |
| E-009B | [x] Raw→validated→metric transforms | E-009A | `interactive_agent:software-engineering` | ETL modules/tests | reproducible datasets | seeded replay equality | E-009A, E-005B | succeeded |
| E-009C | [x] Sample-size/CI/power/SRM library | E-009A | `interactive_agent:analytics` | statistics modules/tests | statistical engine | benchmark fixtures within tolerance | E-009A | succeeded |
| E-009D | [x] Metric freshness/quality dashboard | E-009B/C | `interactive_agent:software-engineering` | `app/metric_dashboard.py`, tests | observable statistics | stale/missing alert tests | E-009B, E-009C | succeeded |
| E-009E | [ ] Study preregistration validator | statistical protocol, E-009A/C | `interactive_agent:analytics` | study validator/tests | valid/blocked study decision | missing protocol field blocks start | E-005C, E-009A, E-009C | blocked |

### WP-E10 — Delivery・operations skeleton

| ID | Work | Input | Execution | Target files | Output | Acceptance | Depends | Initial state |
|---|---|---|---|---|---|---|---|---|
| E-010A | [x] App/environment/dependency skeleton | architecture baseline | `interactive_agent:software-engineering` | app root, lock, `.env.example` | reproducible local app | clean build/test | E-001C | succeeded |
| E-010B | [x] CI・preview・artifact promotion | E-010A | `interactive_agent:devops` | workflow/deploy config/tests | preview delivery | same artifact promotion test | E-010A | succeeded |
| E-010C | [ ] Scheduler・DLQ・health/lag alerts | E-004C, E-010B | `interactive_agent:devops` | scheduler/monitor/tests | observable automation | timeout/DLQ alert test | E-004C, E-010B | blocked |
| E-010D | [ ] Backup/restore・kill switch | E-010C | `interactive_agent:devops` | controls/runbooks/tests | recoverable operations | restore/failure injection drill | E-010C | blocked |
| E-010E | [ ] Phase -1 release readiness | all enabling outputs | `interactive_agent:opsboard` | readiness pack | Ready/Not Ready evidence | DevOps `Ready`＋all Critical closed | E-002D, E-004C, E-005C, E-006F, E-006G, E-006H, E-007D, E-007E, E-007F, E-008C, E-009D, E-009E, E-010D | blocked |

## 8. Current Ready Queue

現時点で開始可能なのは以下。

1. `E-004C` — Retry/backoff/resume/reconcile（`E-004B`succeeded後に解放）
2. `E-005C` — Evidence validator・completion hook（`E-004B`succeeded後に解放）
3. `E-006G` — Legal evidence/expiry dashboard（`E-009D`succeeded後に解放）
4. `E-006H` — Spend/cap dashboard（`E-009D`succeeded後に解放）

`E-002D`, `E-002C`, `E-004B`, `E-009D` はsucceededへ遷移済み。上記4件は依存完了済み。これ以外を先行実行してはならない。

## 9. Definition of Done

- `task_manifest.yaml`がschema validation、ID uniqueness、dependency existence、cycle checkに合格する。
- Initial Ready Queueの3件に実在するexecution commandとacceptance commandがある。
- 全blocked taskにblocking dependencyがある。
- Human日常作業がportal/MA/policy/exception workflowへ割り当てられている。
- Statistical tasksが共通protocolを入力として持つ。
- Phase -1完了時、OpsBoardとDevOpsが`Ready to Start Business Phase 0`を独立判定する。
