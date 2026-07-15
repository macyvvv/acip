# PROJECT

## Mission

Build an AI Native Company.

## Vision

Knowledge First

Platform Independent

Human Approval Minimal

GitOps

## Current Phase

Phase 3

Business Agent Automation Platform live (Levels 0-3a/3c; Level 3b built
per `adr/ADR-0038` but not yet wired to cron/launchd). Governance Layer
Overhaul (`adr/ADR-0037`) complete as of its 2026-07-14 addendum.

## Current Repository

GitHub

Canonical

## Current Objective

Clear the real operational backlog Level 3b's unwired scheduler left
behind, and keep the platform's two now-parallel structures --
`system/agent_runtime/role_prompts/*.md` (automated-execution authority)
and `.claude/agents/*.md` (interactive-session authority, `adr/ADR-0039`)
-- from silently drifting, while continuing the platform's roadmap
(see Current Priority) with the same discipline that closed out
ADR-0037: name the real concern, keep every genuinely enforced safety
property intact (PR-required workflow, human approval gate, Level 3a/3c's
real spend caps, secret-handling discipline), and review each change
against global optimization, not just the task at hand.

## Current Priority

1 **Phase A (immediate, low-cost)** -- Triage the 15 stalled `candidate`
tasks in `system/runtime/business_agent_tasks/queue.json` (mostly
`kabukicho_survival_map` Level-1 auto-triggers never executed); decide,
per task, execute or discard. Decide Level 3b's cron/launchd wiring
question explicitly (currently built but unscheduled -- neither "on" nor
"deliberately off" is recorded anywhere). Document the `.claude/agents/`
Ops layer (8 business roles + 6 Ops + `opsboard`, added 2026-07-14) in
`CLAUDE.md`/`AGENTS.md`, which currently don't mention it at all.

2 **Phase B (short-term)** -- Stabilize the free-tier `claude_invocation`
roles (`market_research`/`marketing`/`doc_creation`/`scenario_writing`/
`pdca`/`analytics`) across `text_syndicate` (continuous-content cadence)
and `kabukicho_survival_map` (low-frequency, site-type). Periodically
audit that ADR-0039's dual-authority sync rule (edit both role
definitions together when they diverge on substance) is actually being
followed.

3 **Phase C (mid-term)** -- Explicit, capped, human-approved go-ahead
before enabling `somia`'s paid `image_generation`/`video_generation`
roles. Begin `music_platform`'s greenfield build (closed/deleted
PRODUCT-0002, explicitly revived). Begin `dreamcore_video` (DreamCore系
動画) and `physics_math_visualization` (物理数学定理ビジュアライゼーション)
greenfield builds -- both are red-ocean markets with universal demand;
differentiation axis is production quality and, for physics/math,
faithfulness to first principles where existing content is weak.

4 **Phase D (long-term)** -- Full multi-agent-fleet automation across all
6 businesses (`kabukicho_survival_map`, `somia`, `text_syndicate`,
`music_platform`, `dreamcore_video`, `physics_math_visualization`), PDCA
closing the loop on real analytics data, human involvement converging
toward strategy/approval/capital allocation only -- each further
reduction of human approval still requires its own ADR, per the existing
Level 3 sequencing discipline.

## Decision Rule

Global Optimization

over

Local Optimization

Name the real underlying concern (cost, irreversibility, determinism,
secrets) in any new rule, rather than writing an unqualified absolute --
see `adr/ADR-0037` for why this was added as an explicit convention.

## Human Responsibility

Strategy

Approval

Capital Allocation

## Claude Code Responsibility

Architecture

Implementation

Refactoring

Testing

Review

Pull Request authorship

This repo used to split this work between ChatGPT (architecture/review)
and Codex (implementation/PR) because neither tool retained context across
sessions. Claude Code holds a continuous session and executes directly, so
that split is gone -- see `CLAUDE.md`'s "Operating model" section.

## Success KPI

Human Approval Time

< 5 min / day

Knowledge Asset Growth

Continuous

Repository

Canonical

## Next Action

Update automatically when Phase changes.