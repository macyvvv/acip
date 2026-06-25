# EP-0103 Validation

## Primary Validation

```bash
python scripts/validate_ep_0103.py
```

## Regression Validation

```bash
python scripts/validate_ep_0102.py
python scripts/validate_ep_0101.py
python scripts/validate_ep_0100.py
```

## Expected Result

All commands exit with status 0.

## Required Checks

`validate_ep_0103.py` must verify:

- required contract files exist
- required worker profiles exist
- spec lifecycle directories exist
- worker routing file exists
- contract text preserves Human Boundary
- Codex profile requires explicit specification before changing existing runtime implementation
- no runtime external execution is introduced
