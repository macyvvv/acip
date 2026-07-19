# Architecture — Frozen

```text
Specification
  ├─ character schema
  ├─ sampling policy
  └─ runtime policy
        ↓
Planning
  ├─ deterministic plan
  ├─ target buckets
  └─ prompt inputs
        ↓
Generation
  ├─ prompt renderer
  ├─ OpenAI Images adapter
  └─ immutable raw store
        ↓
Validation
  ├─ technical validation
  ├─ duplicate detection
  ├─ review record
  └─ coverage report
        ↓
Export
  ├─ accepted images
  ├─ captions
  ├─ manifest
  └─ provenance
```

SQLiteは実行状態、JSONLは監査ログ、filesystemは画像正本に用いる。
