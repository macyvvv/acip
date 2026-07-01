# VALIDATION_COMMAND_POLICY

## Purpose
This document defines the canonical validation commands for this repository and how operators should choose the correct Python interpreter.

The repository policy is stable.
Local shell defaults are not.
Interpreter-specific availability of `pytest` is not guaranteed.

## Canonical Commands

### Canonical `validate_all`
```bash
python3 system/scripts/validate_all.py
```

### Canonical pytest command
Use the known-good interpreter command that has `pytest` available:
```bash
/Library/Developer/CommandLineTools/usr/bin/python3 -m pytest -q
```

## Interpreter Policy
Validation must be run in a known-good interpreter environment.

Do not assume that the `python3` on the current shell path has `pytest` installed.

## How to detect the active interpreter
```bash
python3 -c 'import sys; print(sys.executable)'
```

## How to check whether `pytest` is available
```bash
python3 -c 'import importlib.util; print(importlib.util.find_spec("pytest") is not None)'
```

If this prints `False`, `python3 -m pytest -q` will fail in that interpreter.

## What to do when `python3 -m pytest -q` fails
1. Do not change repository files to work around the interpreter.
2. Switch to a known-good interpreter that already has `pytest`.
3. Re-run validation with that interpreter.

Example:
```bash
/Library/Developer/CommandLineTools/usr/bin/python3 -m pytest -q
```

## Repository Policy vs Local Machine Behavior
- Repository policy: `python3 system/scripts/validate_all.py` is the canonical repository validation entrypoint.
- Local machine shell defaults: may point to an interpreter without `pytest`.
- Interpreter-specific availability of `pytest`: must be checked before running pytest.

## Operator Rule
Validation must be executed in a known-good interpreter environment.

If the active interpreter is missing `pytest`, the operator must use a different interpreter rather than assuming repository failure.
