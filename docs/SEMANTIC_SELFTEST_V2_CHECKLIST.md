# Semantic SelfTest v2 Checklist

## Checklist

| ID | Check | Expected |
|---|---|---|
| V2-01 | Config exists | `selftest.yml` |
| V2-02 | Archive excluded from canonical duplicates | archive duplicates are ignored |
| V2-03 | Drafts excluded from dead-doc failure | draft orphan is not failure |
| V2-04 | Templates excluded from dead-doc failure | templates are not failures |
| V2-05 | Current Objective parser is declaration-only | explanatory text is ignored |
| V2-06 | Boundary check ignores selftest constants | no self-match |
| V2-07 | Workflow-script links are verified | missing scripts fail |
| V2-08 | Secrets still fail | high-confidence secrets fail |

## Definition of Done

Semantic SelfTest v2 is complete when false-positive FAIL count is zero while real boundary, link, secret, and required file violations still fail.
