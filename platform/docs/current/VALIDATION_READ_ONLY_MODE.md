# VALIDATION_READ_ONLY_MODE

`python3 scripts/validate_all.py` is read-only by default and does not refresh repository validation artifacts.

## Rule

- Validation executes checks and prints results.
- Validation does not rewrite runtime validation artifacts unless an explicit refresh command is used.

