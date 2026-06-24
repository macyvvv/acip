# 015 Asset Intake Policy

## Conclusion

Asset intake must convert raw ideas, conversations, observations, and operational needs into reviewable asset candidates without treating raw input as canonical.

## Purpose

Intake exists to prevent useful knowledge from being lost while preserving the rule that repository content, not conversation, is the source of truth.

## Intake Sources

Approved intake sources:

- Human mission statements
- ChatGPT review outputs
- Codex implementation notes
- GitHub issues
- ADR discussions
- operational learnings
- market or platform observations
- reusable prompts
- reusable checklists

## Intake Rules

- Repository overrides conversation.
- Raw intake is not canonical.
- Every intake item must identify its intended asset type.
- Every intake item must state objective, scope, and out of scope.
- Intake must not bypass review.
- Intake must not introduce runtime implementation.
- Intake must not introduce auto posting, scraping, or platform API integration.

## Required Fields

Each intake item must include:

- intake_id
- proposed asset title
- proposed asset type
- source context
- business / operational / learning / strategic value
- revenue link
- scope
- out of scope
- risk notes
- recommended next action

## Done Condition

Asset intake control is complete when intake templates, issue template, review checklist, validation script, and CI workflow exist and pass.
