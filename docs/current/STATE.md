# STATE

## Purpose

This document represents the current runtime state of ACIP.

It should answer:

- Where are we now?
- What is the current priority?
- Who should act next?
- What defines completion?

Long-term principles belong to docs/current/PROJECT.md or basis/.

---

# Current Phase

Phase 3 : Business Agent Automation Platform (Levels 0-3a/3c live) +
Governance Layer Overhaul

---

# Current Milestone

Governance-layer overhaul (`adr/ADR-0037`): retiring ChatGPT/Codex-era
coordination scaffolding and rigid absolute rules that no longer match how
Claude Code actually operates this repository.

---

# Active Epic

Governance layer overhaul, staged across several PRs (see
`adr/ADR-0037-governance-layer-overhaul.md`).

---

# Active Issue

None (this work was operator-authorized directly in conversation, not
issue-tracked -- see the ADR for the authorization record).

---

# Active Pull Request

See the governance-overhaul PR sequence merged into `main`; check
`adr/ADR-0037` for the up-to-date list.

---

# Current Blockers

None.

---

# Current Decision

The business-agent automation platform is live in production:
- Level 0-2: task proposal, human approval, per-task-scoped execution.
- Level 3a: policy-based pre-approval (`system/runtime/agent_handoff/
  auto_approval_policy.json`) -- real, capped, human-authored, no fresh
  per-task approval needed for named `(business_id, role_id)` pairs.
- Level 3c: policy-based unattended publishing, same shape as 3a for the
  publish step.
- Level 3b (scheduled/unattended trigger) is explicitly not built --
  requires separate operator sign-off.

Real product surfaces live under `app/products/` (kabukicho_survival_map
with an embedded Google Map + nearest-first list, text_syndicate content
chain, minimal_launch_brief_generator, repository_operational_summary) and
`app/tools/approval_console_mvp`.

GitHub is the Single Source of Truth. Nothing merges to `main` without a
PR; the local pre-push hook (`bash system/scripts/git/install_hooks.sh`)
is the real enforcement today -- see `docs/current/MAIN_PROTECTION_
POLICY.md` for why this is opt-in-per-clone and not backed by native
GitHub branch protection (private repo, free plan).

---

# Next Action

## Actor

Claude Code

## Action

Continue and complete the governance-layer overhaul's remaining stages
(see `adr/ADR-0037` for current progress), then resume normal product work.

## Success Condition

All staged PRs merged, `python -m pytest -q` and `python system/scripts/
validate_all.py` both clean, `adr/ADR-0037` fully records what changed and
what explicitly did not.

---

# Last Updated

2026-07-12

---

# Runtime Notes

## Repository Priority

docs/current/PROJECT.md

↓

docs/current/STATE.md

↓

CLAUDE.md

↓

basis/

↓

adr/

↓

Issue

↓

Pull Request

↓

Conversation

`AGENTS.md` and `.system/` are kept as historical record of the pre-Claude-Code
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

In active revision (`adr/ADR-0037`)

Business Agent Automation Platform (Levels 0-3a/3c)

Live in production

Product Surfaces (`app/products/`)

Multiple real products shipped and iterating
