# 009 Asset Production Policy

## Conclusion

Canonical Asset Production follows a controlled lifecycle: Intake → Draft → Review → Approval → Merge → Reuse.

## Lifecycle

```text
Intake
↓
Draft
↓
CSO Review
↓
Codex Repository Check
↓
Human Approval
↓
Merge
↓
Reuse
```

## Responsibilities

| Stage | Human | ChatGPT | Codex | Repository |
|---|---|---|---|---|
| Intake | A | R | I | Record |
| Draft | A | R | C | Store |
| Review | A | R | C | Evidence |
| Validation | I | C | R | Check |
| Approval | A/R | C | I | Gate |
| Merge | A | I | R | Canonicalize |
| Reuse | A | C | C | Source |

## Production Rules

- Current Objective must not change during production.
- Repository overrides conversation.
- Asset scope must be explicit before review.
- Drafts must separate facts, assumptions, and proposals when relevant.
- Reuse must preserve canonical meaning.
- Platform-specific adaptation must not mutate the source asset.

## Prohibited in Current Phase

- runtime agent execution
- auto posting
- platform API integration
- scraping-dependent production
- approval bypass
- autonomous external actions

## Done Condition

A Canonical Asset is done when it passes the quality gate, receives Human approval, and is merged into `main`.
