# Asset Status Model

## Conclusion

Canonical Assets use a fixed status model to prevent ambiguity.

## Status Values

```text
intake
draft
review
approved
canonical
reuse
revision
deprecated
```

## Transition Rules

| From | To | Required Action |
|---|---|---|
| intake | draft | Create structured asset draft |
| draft | review | Complete required metadata and body |
| review | approved | Pass quality gate and Human approval |
| approved | canonical | Merge into `main` |
| canonical | reuse | Reference canonical asset id |
| canonical | revision | Open revision issue / PR |
| revision | canonical | Merge approved update |
| canonical | deprecated | Add deprecation note and replacement if any |

## Invalid Transitions

- intake → canonical
- draft → canonical
- review → reuse
- deprecated → canonical without revision
- any status → approved without Human approval

## Repository Rule

The status model is descriptive in repository files and enforceable through review and validation scripts.
