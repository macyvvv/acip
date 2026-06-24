# 012 Asset Repository Conventions

## Conclusion

Canonical Assets require predictable paths, naming, and metadata so they can be reviewed, reused, and audited without relying on chat memory.

## Directory Conventions

```text
assets/
  knowledge/
  content/
  media/
  operational/
  index/
```

## File Naming

Use lowercase kebab-case.

```text
assets/knowledge/<asset-id>-<short-title>.md
assets/content/<asset-id>-<short-title>.md
assets/media/<asset-id>-<short-title>.md
assets/operational/<asset-id>-<short-title>.md
```

## Asset ID Convention

```text
KA-0001  Knowledge Asset
CO-0001  Content Object
MO-0001  Media Object
OA-0001  Operational Asset
```

## Required Front Matter

```yaml
asset_id:
title:
asset_type:
status:
owner:
version:
source_context:
audience:
related_adr:
related_wbs:
risk_level:
last_reviewed:
```

## Repository Rules

- `assets/index/` tracks discoverability.
- Canonical source lives in `assets/`, not in chat.
- Derived outputs must reference source asset id.
- Temporary drafts may live in PR branches but are not canonical.
- Runtime implementation is not introduced by these conventions.

## Prohibited

- ambiguous asset names
- unversioned canonical edits
- reuse without source reference
- deleting canonical history to hide prior decisions
- approval bypass
