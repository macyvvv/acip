# ACIP SelfTest Import Fix Pack

## Conclusion

This pack fixes the `ImportError: cannot import name 'fail' from 'selftest_common'`.

## Cause

Some existing selftest modules still import `fail`, while the remediation pack renamed the function to `issue`.

## Fix

`selftest_common.py` now exposes `fail()` as a backward-compatible alias to `issue()`.

## Validation

Run:

```bash
python scripts/selftest/validate_repository_selftest_complete.py
```
