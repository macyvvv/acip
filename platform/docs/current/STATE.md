# STATE

## Purpose

This document represents the current runtime state of ACIP.

It should answer:

- Where are we now?
- What is the current priority?
- Who should act next?
- What defines completion?

Long-term principles belong to platform/docs/current/PROJECT.md or platform/basis/.

---

# Current Phase

Phase 3 : Business Agent Automation Platform (Levels 0-3a/3c live, 3b
built but unscheduled) -- Governance Layer Overhaul complete
(`platform/adr/ADR-0037`, incl. 2026-07-14 addendum)

---

# Current Milestone

Roadmap Phase A (see `platform/docs/current/PROJECT.md`'s Current Priority):
clear the 15-task Level-3b backlog, decide the cron/launchd wiring
question, and keep the `.claude/agents/` interactive layer documented and
aligned with ADR-0039/ADR-0041.

---

# Active Epic

Business Agent Automation Platform roadmap, Phase A of 4 (see
`platform/docs/current/PROJECT.md`). Governance layer overhaul
(`platform/adr/ADR-0037-governance-layer-overhaul.md`) is complete, not active.

---

# Active Issue

None (this work was operator-authorized directly in conversation, not
issue-tracked -- see the ADR for the authorization record).

---

# Active Pull Request

See the governance-overhaul PR sequence merged into `main`; check
`platform/adr/ADR-0037` for the up-to-date list.

---

# Current Blockers

None.

---

# Current Decision

The business-agent automation platform is live in production:
- Level 0-2: task proposal, human approval, per-task-scoped execution.
- Level 3a: policy-based pre-approval (`platform/system/runtime/agent_handoff/
  auto_approval_policy.json`) -- real, capped, human-authored, no fresh
  per-task approval needed for named `(business_id, role_id)` pairs.
- Level 3c: policy-based unattended publishing, same shape as 3a for the
  publish step.
- Level 3b (scheduled/unattended trigger, `platform/adr/ADR-0038`): the runner
  (`platform/system/scripts/business_agent/run_scheduled_execution.py`) and its
  kill switch are built, but nothing invokes it on a schedule yet -- no
  cron/launchd entry exists. Real consequence: 15 `candidate` tasks sit
  stalled in `platform/system/runtime/business_agent_tasks/queue.json`. Whether to
  wire it up or deliberately leave it manual-trigger-only is an open
  Phase A decision (see `platform/docs/current/PROJECT.md`), not yet made.
- `.claude/agents/*.md`: 15 specialist roles + 9 Ops agents + `opsboard`
  (25 interactive roles). ADR-0041 added interactive-only BusinessOps,
  ProductOps, LegalOps and seven specialists; they do not expand unattended
  authority. The original eight business-content roles still run parallel
  to registry definitions under ADR-0039's dual-authority rule.

Real product surfaces live under `platform/app/products/` (kabukicho_survival_map
with an embedded Google Map + nearest-first list, text_syndicate content
chain, minimal_launch_brief_generator, repository_operational_summary) and
`platform/app/tools/approval_console_mvp`.

GitHub is the Single Source of Truth. Nothing merges to `main` without a
PR; the local pre-push hook (`bash platform/system/scripts/git/install_hooks.sh`)
is the real enforcement today -- see `platform/docs/current/MAIN_PROTECTION_
POLICY.md` for why this is opt-in-per-clone and not (yet) backed by native
GitHub branch protection. This repo is actually public, not private as
previously documented here -- native protection is available for free and
simply hasn't been enabled (operator decision pending, see that doc).

---

# Next Action

## Actor

Claude Code / Human (Level 3b wiring decision needs explicit operator
sign-off, per the standing rule that new autonomy-affecting decisions
aren't self-authorized)

## Action

Work Roadmap Phase A (`platform/docs/current/PROJECT.md`'s Current Priority):
triage the 15 stalled `candidate` tasks in `queue.json`, get an explicit
decision on Level 3b's cron/launchd wiring, and keep the documented
interactive role inventory aligned with its live definitions.

## Success Condition

Zero stale `candidate` tasks left unaddressed (executed or explicitly
discarded with reason), Level 3b's scheduling status recorded as a
deliberate decision either way, `CLAUDE.md`/PROJECT/STATE reference the
live `.claude/agents/` structure, `python -m pytest -q` and
`python platform/system/scripts/validate_all.py` both clean.

---

# Last Updated

2026-07-17

---

# Runtime Notes

## Repository Priority

platform/docs/current/PROJECT.md

↓

platform/docs/current/STATE.md

↓

CLAUDE.md

↓

platform/basis/

↓

platform/adr/

↓

Issue

↓

Pull Request

↓

Conversation

`AGENTS.md` and `platform/.platform/system/` are kept as historical record of the pre-Claude-Code
protocol (see `CLAUDE.md`'s opening section) -- not part of the live
priority chain above.

---

## Adopted Runtime

Claude Code

- Architecture, implementation, review, and PR authorship -- covers what
  ChatGPT (architecture/review) and Codex (implementation/PR) used to do
  separately, before this repo had a tool with continuous context across
  a whole session.

Human

- Strategy
- Approval
- Capital Allocation

---

## Current Repository Status

GitHub Foundation

Completed

Constitution / Governance Layer

In active revision (`platform/adr/ADR-0037`)

Business Agent Automation Platform (Levels 0-3a/3c)

Live in production

Product Surfaces (`platform/app/products/`)

Multiple real products shipped and iterating
