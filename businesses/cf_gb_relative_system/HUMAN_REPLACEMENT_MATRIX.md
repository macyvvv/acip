# Human Replacement Matrix

## Principle

日常の収集・照合・承認・通知・更新をHumanへ依存させない。一回限りのowner policy設定と、法的資格を要する例外だけを外部decision boundaryとして残す。

| Former Human work | Normal path replacement | Data required | Auto decision | Exception |
|---|---|---|---|---|
| interview募集・日程 | Portal＋MA workflow | segment、contact consent、quota | eligible/quota/reminder/close | recruitment failureでRework |
| 同意取得 | Consent page/version ledger | purpose、retention、withdrawal | consentなしは収集不可 | guardian/counsel要件は停止 |
| 回答・店舗確認 | Survey/store verification page | response、identity evidence、timestamp | dedup、completeness、confidence | disputed identityはquarantine |
| coding・集計 | Statistical data plane | raw response、codebook、model/version | registered protocolで集計 | low confidenceは追加sample |
| usability test | Instrumented task page | task event、error、assist、segment | success/CI/stop rule | accessibility defectはblock |
| 品質監査 | Seeded sample＋verification workflow | population、field risk、source evidence | CI/critical-error policy | source conflictはquarantine |
| Gate evidence確認 | Evidence validator＋policy engine | artifact hash、expiry、metric | Go/Rework/Stop | strategy/capital exceptionのみowner |
| 法務条件確認 | Legal registry＋expiry watcher | authority/version/jurisdiction/condition | unknown/expiredはdeny | qualified counselへ送る |
| 費用承認 | Spend policy＋cap ledger | budget、committed、forecast、cash | cap内のみ許可 | cap変更はowner decision |
| 公開判断 | Release policy＋security/QA evidence | signed artifact、severity、rollback | all-greenのみpromotion | Critical/Highは停止 |
| 訂正・削除 | Correction console | claimant、evidence、field、urgency | policy範囲で訂正/非公開 | appeal/legal holdはcounsel queue |
| SLA/reminder | Scheduler/MA | deadline、status、contact policy | reminder/escalate/expire | repeated failureはDLQ |
| 異議申立て | Exception console | original decision、new evidence | deterministic再評価 | policy外はowner/counsel |

## Owner Decisions Retained

- 初期policyの戦略目的・撤退条件
- 費用・損失・risk appetite上限
- 法的資格を要する判断
- policy外の例外受容

これらも材料収集、期限、recordingはsystemが行う。返答がない場合は許可ではなく`quarantined`とする。

## Required System Surfaces

1. Research/consent portal
2. Participant MA workflow
3. Store verification page
4. Instrumented usability page
5. Gate/policy console
6. Correction/exception console
7. Legal evidence/expiry dashboard
8. Spend/cap dashboard
9. Statistics and data-quality dashboard

