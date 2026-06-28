# EP-0104 Validation

## Primary

```bash
python system/scripts/validate_ep_0104.py
```

## Regression

```bash
python system/scripts/validate_ep_0103.py
python system/scripts/validate_ep_0102.py
python system/scripts/validate_ep_0101.py
python system/scripts/validate_ep_0100.py
```

## Required Checks

- EP contract schema exists.
- EP contract template exists.
- EP-0104 contract exists.
- Contract loader can read the active EP contract.
- Contract validator can validate required fields.
- Regression validation remains green.
