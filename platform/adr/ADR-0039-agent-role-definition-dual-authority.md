# ADR-0039: Agent Role Definitions Have Two Authorities — Document, Don't Delete

## Status

Accepted

## Triggering Incident

A repo-wide consultation (2026-07-14: all 15 acip subagents under
`.claude/agents/` — the 8 business-content roles + 6 Ops + `opsboard` —
each asked independently whether acip's current process/refactoring needs
were fine as-is) surfaced a live discrepancy nobody had previously
written down: this repo defines its 8 business-content agent roles
(`market_research`, `marketing`, `doc_creation`, `scenario_writing`,
`pdca`, `image_generation`, `video_generation`, `analytics`) **twice**,
in two independently-maintained places, with no documented statement of
which one governs.

Several roles found this on their own. `market-research`'s and
`marketing`'s consultation reports independently noticed that
`platform/system/agent_runtime/role_prompts/*.md` (the legacy prompt template) and
`.claude/agents/*.md` (the new Claude Code subagent definition) disagree
on a real, consequential point — who writes the output artifact — not
just cosmetic wording drift. `doc-creation`'s report found the same
pattern. `dataops`'s report went further and confirmed, by reading the
actual execution code, that the legacy side is not dead: it is the live
backbone of the automated (Level 3a/3c) business-agent execution
pipeline. `modelops`'s report independently confirmed the same thing from
the model-selection angle. `opsboard`'s synthesis called out that the
`.claude/agents/*.md` files' own reporting-line claims about each other
had already drifted (see the separate market-research→DataOps fix made
the same day), which is exactly the kind of silent divergence two
unreconciled copies of the same fact produce over time.

This matters more than an ordinary duplication because CLAUDE.md already
names this: *"This repo already has a duplication problem"* — but that
line was written before `.claude/agents/*.md` existed. It's now the
newest instance of the pattern, and unlike some of ADR-0037's cleanup
targets, **both copies here are actually live**, so the fix is not
"delete the dead one."

## Current Design

Two independent definitions of the same 8 roles exist side by side:

1. **`platform/system/agent_runtime/role_prompts/*.md`** + machine-generated
   `platform/system/runtime/agent_roles/agent_role_registry.json` (source:
   `platform/system/core/agent_role_registry.py`). Confirmed live: it is imported
   directly by `platform/system/orchestrator/business_agent_execution_adapter.py`
   (`from system.core.agent_role_registry import get_role`), which reads
   each role's `model_capability` field and resolves it to a real
   `claude -p --model ...` invocation via `_resolve_model()`
   (`business_agent_execution_adapter.py:81,155-162`), and is the role
   registry `platform/system/core/business_agent_trigger.py` and
   `execution_pre_approval_policy.py` route Level 3a/3c automated
   execution through. This is the production backbone for
   automated/unattended business-agent execution.

2. **`.claude/agents/*.md`** — 8 files added 2026-07-14 as native Claude
   Code subagent definitions, so the same 8 roles (plus the 6 new Ops
   roles and `opsboard`) can be invoked directly inside an interactive
   Claude Code session (via the `Agent` tool or a slash-command-driven
   workflow), without going through the execution adapter at all.

Neither file set references the other. Nothing states which is
authoritative if their instructions diverge — and per the triggering
incident, they already have (conflicting statements on who writes the
output artifact; a reporting-line claim in `market-research.md` that
disagreed with three other files before being fixed the same day this
ADR was written).

## Decision

Both copies stay. Neither is deleted, and neither is demoted to a thin
pointer at the other, because they serve genuinely different execution
paths that are not interchangeable today:

- The registry-driven pair (`role_prompts/*.md` + `agent_role_registry.json`)
  is the only one wired into unattended/automated execution
  (`business_agent_execution_adapter.py`, the pre-approval policy, model-tier
  resolution). Collapsing it into `.claude/agents/` would require rebuilding
  that entire adapter to read Claude Code subagent frontmatter instead of the
  registry's JSON shape — out of scope here, and not something this
  consultation's findings justify on their own.
- `.claude/agents/*.md` is the only one usable directly inside an
  interactive Claude Code session (including by `opsboard` and the 6 Ops
  roles, which have no registry-side equivalent at all — they are
  Claude-Code-only by design).

Instead:

1. **`platform/system/agent_runtime/role_prompts/*.md` + `agent_role_registry.json`
   is authoritative for automated/unattended execution** (Level 3a/3c,
   model-tier resolution, pre-approval policy). Any change to a role's
   allowed tools, output contract reference, or IO permissions that must
   hold during unattended execution changes here first.
2. **`.claude/agents/*.md` is authoritative for interactive Claude Code
   use** (this ADR does not change that), and should be kept
   *consistent in substance* with its registry-side counterpart for the
   8 shared roles — same IO permissions, same output contract reference,
   same artifact path convention — even though the file format differs
   (frontmatter + free prose vs. templated prompt + JSON schema).
3. When the two disagree on a substantive point (not wording, but an
   actual instruction — read-only vs. write, which contract applies,
   which role it reports to), fix both in the same change. Do not treat
   either as free to drift because "the other one is real." The
   2026-07-14 market-research reporting-line fix is the model to follow:
   found via cross-file inconsistency, corrected in all files that
   referenced it, same commit.
4. This dual-authority arrangement is temporary scaffolding, not a
   permanent design goal. If/when the execution adapter is rebuilt to
   read `.claude/agents/*.md` directly (or the reverse — Claude Code
   subagents generated from the registry), that project gets its own ADR
   and this one is marked superseded.

## Reason for Change

CLAUDE.md's existing duplication-check rule ("search for an existing
equivalent before adding a new doc/script/workflow, extend/fix instead of
duplicating") assumes duplication is avoidable. Here it wasn't: the two
definitions solve different problems (unattended execution vs.
interactive session ergonomics) that don't currently share a mechanism.
Declaring one dead and deleting it would break the one still driving
real automated execution; pretending they're the same thing and letting
them silently diverge is what already produced a real, if small, bug
(the reporting-line inconsistency). The honest fix is to name which
authority governs which execution path and require both to be updated
together when they overlap — not to force a false single-source-of-truth
that the current architecture doesn't support yet.

## What This Does Not Do

- Does not rebuild `business_agent_execution_adapter.py` to read
  `.claude/agents/*.md` — a real, larger project, out of scope here.
- Does not add tooling to auto-detect drift between the two file sets.
  Doing this by discipline (rule 3 above) first; a lint/CI check is a
  reasonable future addition once the pattern of drift (if it recurs)
  justifies the cost — not preemptively.
- Does not resolve whether the 6 new Ops roles or `opsboard` should ever
  get a registry-side equivalent — per `opsboard`'s own consultation
  finding, most of the 8 business-content roles have barely been
  exercised for real yet (only ~4 of 8 have any runtime artifact history
  at all), so extending the registry side to roles that don't need
  unattended execution would be premature structure.

## Impact Scope

- No files moved or deleted by this ADR itself.
- Fixed same-day, referenced here as the motivating example: `market-research.md`'s
  reporting line, and `marketing.md`'s description of the research→marketing
  chain (see commit "Fix market-research reporting line: MarketingOps -> DataOps").
- Establishes the authority-and-sync-obligation rule above for all future
  edits to either file set.

## Migration Cost

None (documentation-only). Ongoing cost is the discipline in rule 3:
any future edit to a shared role's IO/contract/tool permissions must
touch both file sets in the same change, verified by re-reading both
before considering the change complete.

## Recommendation

Accepted. Revisit if either execution path is rebuilt to consume the
other's definition directly, at which point this ADR should be marked
superseded by whichever ADR records that unification.
