# Statistical Protocol Contract

## Purpose

調査、品質監査、UX、SEO、Affiliate、実験を件数ではなく推定精度と意思決定riskで設計する共通入力契約。

## Required Study Registration

各studyは開始前に以下をmachine-readableに登録する。

| Field | Requirement |
|---|---|
| `study_id` | immutable unique ID |
| `question` | 判断可能な単一の問い |
| `population` | 推論対象 |
| `sampling_frame` | 抽出可能な母集団とcoverage limitation |
| `unit` | user/store/field/session/page等 |
| `strata` | 事前層化と最低層別数 |
| `primary_estimand` | proportion/mean/difference/rate等 |
| `primary_metric` | 算式、分母、window、timezone |
| `precision_or_effect` | CI half-widthまたはMDE/non-inferiority margin |
| `alpha_power` | hypothesis test時のalpha/power |
| `sample_size_method` | 算式/library/version/input |
| `missingness` | 欠測・脱落・late data処理 |
| `multiplicity` | 多重比較補正またはprimary固定 |
| `stopping_rule` | 固定N、precision到達、逐次rule |
| `seed` | 抽出・assignment再現seed |
| `exclusions` | 事前除外と理由 |
| `analysis_code_version` | commit/artifact hash |

## Protocol Types

### Qualitative discovery

- 初期件数はquotaではなく開始点。
- segment別codebookを固定し、新規theme率と反証themeをsession順に記録する。
- saturationは「連続k件で新規primary themeなし」等の事前ruleで判定する。
- interview件数を市場比率の推定へ流用しない。

### Accuracy / zero-critical-error audit

- field risk別に母集団と抽出を分ける。
- 0 errorでも片側上限を報告する。`n`なしの「0件」は合格証拠にならない。
- major error上限目標から必要`n`を逆算する。
- source/category/regionで層化し、seedと対象IDを保存する。

### Usability / task success

- primary task、segment、成功定義、moderation、assist ruleを固定する。
- point estimateと片側/両側CIを報告する。
- 80%等の閾値は必要sampleと許容下限を併記する。
- small formative testとrelease acceptanceを分離する。

### A/B and non-inferiority

- MDEまたはnon-inferiority margin、alpha、power、assignment unit、期間を事前登録する。
- SRM、instrumentation failure、contamination時は無効とする。
- optional stoppingを禁止し、逐次design時だけ承認済み境界を使う。
- primary以外はexploratoryと表示し、多重比較を処理する。

### SEO / Affiliate time series

- seasonality、campaign、algorithm change、reporting delay、approval/cancellation lagを保持する。
- Affiliateは`occurred/pending/approved/paid/reversed/cancelled`を別stateで保存する。
- provider欠損・late arrivalはdata cutoffとrevision historyを伴って再計算する。
- organic session、bot、internal traffic、attribution windowをversion管理する。

## Automated Validation

Studyは以下なら開始不可。

- population、frame、estimand、precision/effect、stopping ruleのいずれかが欠落
- sample size計算の入力・versionがない
- primary metricが複数で優先順位がない
- missingnessまたはlate data policyがない
- random assignmentを使うのにseed/assignment unitがない

## Output Contract

結果はestimate、standard error、CI、sample size、missing/excluded count、protocol deviation、code/data version、decision status (`valid/invalid/inconclusive`) を含む。`invalid`や`inconclusive`を成功へ昇格しない。

