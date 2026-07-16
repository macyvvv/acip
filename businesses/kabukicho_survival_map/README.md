# kabukicho_survival_map

Business canonical root.

## Canonical layout

- `app/`: product source of truth for the static web app
- `app/data/`: business-owned editable DB plus local copies for the app
- `app/scripts/`: business-owned data maintenance commands
- `app/tests/`: product regression checks

## Compatibility boundary

- `platform/app/products/kabukicho_survival_map` remains only as a compatibility symlink to `app/`
- `platform/system/runtime/data/kabukicho/` remains the runtime/distribution JSON source consumed by platform-level automation
- `platform/web/public/kabukicho_survival_map/` remains a generated deploy bundle, not an editing surface

## Primary commands

- Build local + public bundle:
  `python3 businesses/kabukicho_survival_map/app/build.py`
- Validate schema/build output:
  `python -m pytest businesses/kabukicho_survival_map/app/tests/`
- Validate map/list logic:
  `node businesses/kabukicho_survival_map/app/tests/test_app_logic.js`
