# ACIP Repository Semantic SelfTest v2 Pack

## Conclusion

This pack replaces raw lint-style SelfTest behavior with configuration-driven semantic analysis.

## Why

The prior SelfTest correctly found real missing files and boundary risks, but it also produced false positives:

- archived files counted as duplicate canonical ADR/WBS
- explanatory mentions of Current Objective counted as drift
- drafts/templates/reports/indexes counted as orphan documents
- selftest scripts matched their own prohibited keyword constants

## Validation

```bash
python scripts/selftest_v2/validate_semantic_selftest.py
```

Compatibility:

```bash
python scripts/selftest/validate_repository_selftest_complete.py
python scripts/validate_repository_selftest.py
```

## Configuration

`selftest.yml`

## Human Boundary

Human should receive only decision-ready reports. Routine repository inspection should be delegated to SelfTest, Codex, ChatGPT, GitHub Actions, or future approved automation.
