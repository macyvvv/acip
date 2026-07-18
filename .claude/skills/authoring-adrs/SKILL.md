---
name: authoring-adrs
description: How to write a new platform/adr/ entry in this repository -- section structure, numbering, cross-referencing, and the duplicate/scope check CLAUDE.md requires before adding one. Use whenever a change affects architecture, governance, responsibility boundaries, workflow, data model, or runtime behavior (CLAUDE.md's own trigger list) and needs an ADR, not just when told "write an ADR."
---

# Authoring an ADR in this repository

## Before writing one at all

1. **Confirm it's actually ADR-shaped.** Per `platform/adr/README.md`:
   ADRs record *why a decision was made* (durable architecture/governance
   decisions), not runbook steps, checklists, or status snapshots -- those
   belong in `platform/docs/`, and reusable procedures belong in
   `.claude/skills/`. If what you're writing is "how to do X," it's a
   skill, not an ADR.
2. **Check for an existing equivalent first** (CLAUDE.md hard rule): grep
   `platform/adr/` for related prior decisions before adding a new file --
   this repo already has 30+ ADRs and duplication is a known problem. If a
   prior decision is being extended rather than replaced, prefer adding an
   "Amendment" section to the existing ADR over creating a new one (see
   `platform/adr/ADR-0045-creativeops-art-department.md`'s two Amendment
   sections for the pattern).
3. **Architecture/governance/workflow/data-model/runtime changes require
   stopping to confirm with the operator before proceeding** (CLAUDE.md
   hard rule) -- don't write the ADR as a fait accompli of unreviewed work.

## File naming and location

`platform/adr/ADR-NNNN-short-kebab-case-title.md` -- NNNN is the next
sequential number (check the highest existing number in `platform/adr/`
first; don't reuse or guess).

## Section structure (the pattern every recent ADR in this repo follows)

```markdown
# ADR-NNNN: Title

## Status
Accepted by operator approval on YYYY-MM-DD. (Or: Proposed, pending
operator decision -- if not yet confirmed.)

## Context
What situation/incident/gap made this decision necessary. Cite concrete
evidence (specific files, specific incidents this session or in commit
history) rather than asserting the problem abstractly.

## Decision
The actual decision, stated plainly.

## Execution Authority
(If the ADR creates/changes a role or automated capability) What this
role/mechanism can and cannot actually do -- especially any hard tool or
invocation-boundary limits (e.g. "subagents cannot invoke other
subagents").

## Boundaries
Explicit scope limits -- what this decision does NOT cover, to prevent
scope creep being read into it later.

## Consequences
What changes as a direct result -- files added/modified, roles added,
follow-on obligations (e.g. "future X must now also do Y").

## Rejected Alternatives
Other options considered and why they weren't chosen -- this is what
lets a future reader know the decision wasn't arbitrary.

## Validation
How to check this decision was actually implemented correctly (e.g.
"run these tests," "grep for this pattern").
```

Not every section is mandatory for every ADR (e.g. a pure documentation
reorganization ADR may not need "Execution Authority"), but Context,
Decision, Consequences, and Rejected Alternatives appear in essentially
every ADR in this repo and should default to present.

## After writing

- Sync the same decision into any `platform/basis/` file it affects
  (CLAUDE.md: "設計・要件・アーキテクチャ・運用方針の変更時は該当する
  `platform/basis/` ファイルと `platform/adr/*.md`... を同期する").
  Don't leave the ADR as the only place the decision is recorded if
  `platform/basis/CORE_PRINCIPLES.md` or another basis file makes a
  related claim that the new decision now changes.
- If the decision affects a role's actual capabilities (tools, reporting
  structure, IO contract) and that role has a dual-authority counterpart
  in the unattended/automated registry, sync both per ADR-0039's
  dual-authority rule -- don't assume `.claude/agents/*.md` alone is
  sufficient for a shared role.
