# Somia Dataset Generator v1.2.0

GPT Image APIを用いて、SomiaキャラクターのLoRA学習用データセットを再現可能に生成する。

Specification → Planning → Generation → Validation → Export の5層構成(`basis/architecture.md`参照、凍結済み)。Promptは正本ではなく、Character Specification/Sampling Policy/Runtime Configから毎回導出される派生物。

## v1.2.0の確定範囲(Release Candidate)

- Airi Character Contract 1.1(参照実装。他キャラクターは同一schemaを適用して追加する)
- JSON Schemaによる契約検証
- 契約からのPrompt自動構築
- 決定論的seedによる層化サンプリング(比例配分)、coverage report、bucket最低数検証
- `--resume`: run.jsonの状態(planned/running/failed/partially_completed/completed/exported)とgeneration.jsonlから再開、完了済みslotは再生成しない
- Validation: technical validation(Pillowによる実ファイル検証)、重複検出(sha256)、review.jsonl記録、coverage validation
- Export: acceptedのみ出力。`dataset/{images,captions,metadata}` + `manifest.json`(specification version / runtime config version / policy id / prompt hash / image hash / run id) + `report.json`
- cwd非依存のパス解決(`Path(__file__)`基準、`paths.py`)
- リポジトリルート `.github/workflows/somia-dataset-generator-ci.yml` でinstall/ruff/pytest(coverage>=80%)/validate/plan/generate --dry-run を実行

Airiの正本上の髪型は **short-to-medium layered wolf cut**。長髪は自動棄却条件。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

## 契約検証

```bash
python -m somia_dataset_generator validate --character airi
```

期待出力:

```text
valid: airi
```

## APIを呼ばない計画生成

```bash
python -m somia_dataset_generator plan --character airi --count 40
python -m somia_dataset_generator generate --character airi --count 40 --dry-run
```

## 少数実生成

```bash
export OPENAI_API_KEY='...'
python -m somia_dataset_generator generate --character airi --count 3
```

## 中断からの再開

```bash
python -m somia_dataset_generator generate --resume <run_id>
```

完了済み(`status: generated`)のslotは再生成せず、`failed`または未生成のslotのみ再試行する。既に`completed`/`exported`のrunに対しては何もしない。

## Validation → Export

```bash
python -m somia_dataset_generator validate --run-id <run_id>
python -m somia_dataset_generator export --run-id <run_id>
```

`validate --run-id`はtechnical validation・重複検出・coverage検証を行い、`runs/<run_id>/review.jsonl`に採否を記録する。`export`は`review.jsonl`が存在し、acceptedと判定された画像のみを`dataset/`へ出力する(`review.jsonl`が無い状態でのexportはエラーになる)。
