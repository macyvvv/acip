# ADR-0044: Add `trainerops` and a Portable, Repo-Independent Lessons File

## Status

Accepted by operator approval on 2026-07-17.

## Context

Across this session, several real lessons surfaced that were each captured
only where the incident happened to occur, by whichever role happened to
catch it, with no systematic owner:

- The DB-first `poi_db_sync.py`/`build.py` pipeline's data-loss trap (a
  manual JSON edit silently overwritten by a stale DB export) was hit
  *twice* in this repository's history before being written down as a
  Skill (`.claude/skills/syncing-kabukicho-poi-data/`).
- The real `propose_task.py` → `run_scheduled_execution.py` →
  `finalize_content.py` pipeline had to be reverse-engineered from source
  mid-session before it could be documented as a Skill
  (`.claude/skills/running-business-agent-tasks/`).
- `marketingops` self-reported, live, that it lacks the tooling to invoke
  other subagents -- a constraint true of every Ops role's "Agents you
  manage" section, caught in only six of them this session (ADR-0043's
  commit), not systematically audited across all ten.
- The fabricated-first-person-testimonial incident (ADR-0043) was caught
  by chance (the orchestrator reading raw drafts), not by a standing
  process.

CORE_PRINCIPLES.md's own principle #10 already names the general shape of
this problem ("a document or path that once had a real reason to exist
stops being read or executed by anything... nothing removes it... a
periodic \\['does this still match reality?'\\] pass is the durable fix;
not automated as of this writing") but assigns no owner to actually run
that pass.

Separately, the operator wants what Claude learns from operating this
repository to compound into something reusable beyond acip specifically --
not just acip's own governance docs, which are inherently tied to acip's
file layout, business names, and history.

Two distinct needs follow from this, and they are NOT the same thing:

1. A standing owner for capturing lessons *into acip's own governance
   layer* (CORE_PRINCIPLES, ADRs, Skills, and auditing whether existing
   role definitions have gone stale) -- this is fully solvable inside
   acip's existing structure.
2. A genuinely repo-independent artifact the operator can carry into a
   *different* project's own `CLAUDE.md`/skills, where acip's specific
   file paths and business names are meaningless -- this requires a
   separate, deliberately-generic document, because the orchestrator's own
   persistent-memory mechanism is scoped to this one project directory
   (`/Users/ariel/.claude/projects/-Users-ariel-Documents-tools-acip/
   memory/`) and does not itself follow the operator into an unrelated
   project.

## Decision

Add one new interactive Ops role, `trainerops`, and one new portable
artifact.

- **`trainerops`** (cross-cutting, like `secops`/`epistemicsops`): reviews
  what actually happened in a session or across recent commits/incidents
  and distills it into (a) new/updated CORE_PRINCIPLES.md entries, (b)
  new/updated `.claude/skills/` entries, (c) flags on existing role
  definitions that have gone stale or inconsistent (the kind of audit that
  caught the "Agents you manage" inaccuracy, but done systematically
  across all roles rather than incidentally). It writes to acip's own
  governance layer only -- it does not itself decide what's portable.
- **`platform/docs/current/PORTABLE_AGENT_LESSONS.md`**: a deliberately
  acip-independent document. Every entry must be phrased so it makes sense
  with zero acip-specific context (no repo paths, no business names) --
  general operating lessons about working with Claude Code agents/
  subagents/skills that would hold in any project. `trainerops` proposes
  candidate entries when a lesson it captured for acip's own governance
  layer is *also* general enough to belong here; the operator confirms
  before it's added, since portability judgment (is this actually
  acip-independent, or does it just look that way) is exactly the kind of
  judgment call that benefits from a human read, not an automatic one.

## Boundaries

- `trainerops` does not audit content for truthfulness (`epistemicsops`'s
  job) or security exposure (`secops`'s job) -- its lane is specifically
  "did we already learn this and fail to write it down," and "has a
  written-down thing gone stale."
- `trainerops` proposes portable-lessons entries; it does not add them to
  `PORTABLE_AGENT_LESSONS.md` unilaterally -- portability is a judgment
  call the operator confirms, matching this repo's general pattern of
  human-confirmed judgment calls over autonomous ones for anything that
  leaves acip's own boundary.
- Update `opsboard` from ten to eleven Ops.

## Execution Authority

`trainerops` is a `.claude/agents/` interactive-session role only, per the
ADR-0039/ADR-0041/ADR-0043 pattern. Not added to the unattended registry.

## Consequences

Benefits:
- Lessons that were previously captured only incidentally (by whichever
  role/orchestrator happened to notice) now have a standing owner.
- The operator gets an actual, reusable artifact for other projects, not
  just a promise that "Claude will remember" (which the memory system
  cannot deliver across unrelated projects).

Costs:
- An eleventh Ops role (eleven Ops + fifteen specialists + opsboard = 27
  roles) to keep coherent.
- `PORTABLE_AGENT_LESSONS.md` needs periodic pruning of its own, or it
  will accumulate the same kind of governance-layer entropy CORE_PRINCIPLES
  #10 already warns about -- `trainerops` owns that pruning too.

## Rejected Alternatives

- Rely on CORE_PRINCIPLES.md alone: rejected -- it is explicitly acip-
  bound (traces every principle to acip's own code/history), so it cannot
  serve as the portable artifact without a rewrite that would make it
  useless as acip's own record.
- Skip a dedicated role, rely on the orchestrator noticing patterns
  organically: rejected for the same reason ADR-0043 rejected this for
  epistemic auditing -- it worked this session by chance, not by design.
- Make `epistemicsops` own this too: rejected -- epistemicsops's lane is
  auditing content for AI-generated fabrication/overconfidence in the
  moment; trainerops's lane is retrospective, cross-session knowledge
  capture. Different time horizons, different failure modes.

## Validation

- `trainerops` has a unique frontmatter name and cross-cutting reporting
  line.
- `opsboard` recognizes eleven Ops.
- `PORTABLE_AGENT_LESSONS.md` contains zero acip-specific paths/names at
  time of authoring (spot-checked).
- Automated registry remains unchanged.
