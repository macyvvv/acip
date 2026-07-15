# CORE_PRINCIPLES

This is the current, compact record of why this repository is governed the
way it is. It replaces the bulk of what used to be a 44-file `basis/` policy
corpus (see `archive/basis_corpus_2026/README.md` for what was archived and
why) after a full governance-layer review (`adr/ADR-0037-governance-layer-
overhaul.md`) found that almost all of it was pure prose with no enforcing
code behind it, and that several of its rules had gone stale enough to
silently contradict later real decisions.

**Every principle below traces to something either genuinely enforced by
real code today, or genuinely durable (the underlying concern doesn't
change with context).** Nothing here was reinvented from scratch — each
one names its source. If you're about to add a new rule to this corpus,
read the last principle first.

## 1. PR-required; no direct push to `main`

Every change flows through a feature branch and a pull request. Enforced
today by a real local pre-push hook (`system/scripts/git/
prevent_main_push.sh`, activated via `bash system/scripts/git/
install_hooks.sh`) — but that hook lives in `.git/hooks/`, which git never
tracks, so it's opt-in per clone, not automatic. There is no GitHub-side
branch protection configured or available (this repo is private on
GitHub's free plan). See `docs/current/MAIN_PROTECTION_POLICY.md` for the
full, honest enforcement-boundary account — including what a real remote
backstop would need to look like if this gap is ever worth closing further.

*Traces to: real enforcement (the hook) + `CLAUDE.md`'s hard rule (durable
— protects against unreviewed changes reaching production, a concern that
doesn't change with context).*

## 2. Human-in-the-loop before irreversible or costly external-world action

No autonomous execution takes a real, hard-to-undo, external-world action
(a real API call that spends money, a real publish to a real platform, a
real GitHub mutation beyond the reviewed PR flow) without either a
human-authored, capped pre-approval policy or fresh per-task human
approval. This single principle replaces five separate files that used to
restate the identical "Prohibited Until/Before Approval" enumerated list
almost verbatim (`037_autonomous_workflow_policy.md`,
`046_runtime_readiness_boundary.md`,
`068_runtime_integration_boundary_policy.md`,
`070_runtime_dry_run_policy.md`, `072_agent_orchestrator_policy.md`) —
five independent copies of the same concern, drifting independently,
instead of one.

*Traces to: Level 3a/3c's real code and live caps
(`system/core/execution_pre_approval_{policy,state,control}.py`,
`system/runtime/agent_handoff/auto_approval_policy.json`) — genuinely
enforced, gates real subprocess spend today.*

## 3. Approval must be explicit; never inferred from readiness alone

A scope being technically ready to execute is never itself treated as
approval. Approval is a separate, explicit, human-written artifact.

*Traces to: `docs/current/AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT.md`,
already well-calibrated as an absolute rule before this review — this is
the rare case where the existing wording already named a real,
context-independent concern rather than needing a rewrite.*

## 4. The human approval gate is never removable or bypassable

`approval.json`'s `decision_status: approved` field stays exclusively
human-written, for every scope, forever. Level 3a only adds a separate,
additional authorization path consulted when no approval decision exists
at all — it never synthesizes one. This is the one absolute in this
corpus that really is permanent, not a stand-in for something narrower.

*Traces to: `CLAUDE.md`'s "Human keeps: strategy, approval, capital
allocation" (durable by design).*

## 5. Secrets are never committed; injected via local config, never hardcoded

A key that must ship to a browser (like a Maps JavaScript API key) still
never lands in git history — it's generated from a local, gitignored
`.env` into a local, gitignored config file at build time, and kept out of
any committed, deployable bundle. A key that's a genuine server-side
secret never leaves the operator's own environment.

*Traces to: the real, working pattern built this session
(`app/products/kabukicho_survival_map/build.py`'s
`_write_local_gmaps_config()`) + `selftest_v2/semantic_checks.py`'s
secret-boundary check, enforced in CI today.*

## 6. Cost/scope limits for autonomous execution are concrete and checkable, not prose absolutes

When something needs a limit, the limit is a real number in a config file
that code actually reads and enforces (a daily cap, a role restriction),
not a paragraph asserting a boundary that nothing checks. This is also the
structural fix for the incident that triggered this whole review: a rule
written as an unqualified "no X" goes stale silently; a rule written as a
named, checkable limit gets revisited when the limit's premise changes.

*Traces to: `auto_approval_policy.json`'s live per-`(business_id, role_id)`
daily caps — real, enforced, re-validated against the live role registry
on every single evaluation, not just at authoring time.*

## 7. Before adding a new governance doc/script/workflow, check for an existing equivalent first

Extend or fix what's already there instead of creating a parallel,
independently-drifting copy.

*Traces to: `CLAUDE.md`'s own rule — proven valuable twice in the same
session that produced this review: an unwired `check_secret_boundary.py`
and a wired `semantic_checks.py` both had the identical regex bug,
independently; a `repository-selftest-complete.yml` workflow turned out to
be a byte-for-byte duplicate of `repository-semantic-selftest-v2.yml`
under a different name.*

## 8. Architecture- or governance-affecting changes get an ADR

*Traces to: `CLAUDE.md`'s hard rule — stated honestly here as a followed
convention, not a claimed mechanical gate: no script today checks that a
given change has a corresponding ADR. If that ever needs to become a real
enforced check, it doesn't exist yet.*

## 9. Name the real concern, not a bare absolute ban

When writing a new rule, ask: is this durable (the concern holds regardless
of context, like "don't let unreviewed code reach production"), or is it
really a stand-in for something narrower (cost, irreversibility,
determinism, secrets) that should be named directly? An unqualified "no
external API calls" or "no X" reads as permanent even when the real intent
was "avoid unnecessary cost right now" — and nothing forces it to be
revisited when a later real decision needs to cross it. Name the concern,
and the rule stays honest as circumstances change instead of quietly going
stale.

*Traces to: the triggering incident for this entire review — see
`adr/ADR-0037-governance-layer-overhaul.md`.*

## What's still standalone in `basis/`, not folded in here

- [`057_boundary_validation_policy.md`](057_boundary_validation_policy.md)
  — maps to real, distinct enforcement
  (`system/scripts/selftest/check_boundaries.py`, wired into
  `boundary-validation.yml`) with enough specific detail to be worth its
  own file rather than compressing into a principle above.
- [`REPOSITORY_CONVENTIONS.md`](REPOSITORY_CONVENTIONS.md) — actively used
  naming-convention reference (SSOT statement, `UPPER_SNAKE_CASE` docs /
  `lower_snake_case` code convention).

Everything else that used to live in `basis/` is archived at
`archive/basis_corpus_2026/`, with a README there mapping each archived
file to whichever principle above (or piece of still-live code) actually
covers its real content.
