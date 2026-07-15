# ISSUE_PORTFOLIO_ROADMAP

## Purpose
Define the canonical portfolio view for tracked repository work so operators can distinguish `NOW`, `NEXT`, `LATER`, and `FROZEN` before deciding what enters the one-shot approval flow.

## Governance Rule
The issue portfolio roadmap is the planning layer. Approval candidates are a filtered execution layer downstream of the roadmap, not a substitute for it.

## Buckets
- `NOW`: one-shot-ready work that is safe, narrow, and currently actionable.
- `NEXT`: work that should follow the current `NOW` item when capacity opens.
- `LATER`: valid work that is not one-shot-ready under the current baseline.
- `FROZEN`: completed, archived, or historical work that remains visible for governance but must not re-enter active approval flow.

## Execution Fit
- `one_shot_ready`
- `not_one_shot_ready`
- `blocked`
- `completed`
- `archived`

## Classification Summary
- Issue count: 37
- NOW: 1
- NEXT: 0
- LATER: 5
- FROZEN: 31

## One-Shot-Ready Issues
- Issue #41: `PRODUCT-0004 Product Launch Follow-up`

## Portfolio Notes
- Completed issues remain visible in roadmap history, but they are excluded from the active approval candidate flow.
- Broad architecture, large infra, and operator-control work remain visible in the roadmap but are not promoted into the Approval Console unless explicitly narrowed and reclassified.
- `NOW` items are the only items eligible to become recommended approval candidates under the current one-shot baseline.

## Runtime Artifacts
- `system/runtime/roadmap/issue_portfolio.json`
- `system/runtime/roadmap/issue_portfolio.md`

## Source Inputs
- `system/runtime/github/open_issues.json`
- `system/runtime/issues/completed/`
- `system/runtime/research/issue_creation_drafts.json`
- `docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md`
- `docs/current/ISSUE_OPERATOR_QUICKSTART.md`
- `docs/current/ISSUE_CENTRIC_OPERATION.md`
