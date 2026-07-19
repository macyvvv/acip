# Somia Dataset Generator v1.1.0

GPT Image APIを用いて、SomiaキャラクターのLoRA学習用データセットを再現可能に生成する。

## v1.1.0の確定範囲

- Airi Character Contract 1.1
- JSON Schemaによる契約検証
- 契約からのPrompt自動構築
- Sampling Policyとの整合性検査
- Airi参照画像manifest

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
