# CLAUDE.md

This file replaces the ChatGPT+Codex boot ritual (`AGENTS.md`, `.system/BOOT.md`,
`.system/REVIEW.md`, `.system/DECISION.md`, `.system/STYLE.md`) as the operating
instructions for this repository. Those files are kept as historical record of
the old protocol; do not follow their response-format rituals (forced
Conclusion/Next Action ordering, mandatory "Current Phase:" footer, single-step
hand-holding). They existed to compensate for ChatGPT and Codex having no
shared memory across sessions. Claude Code holds this file and the
conversation directly, so that ceremony is dropped.

## What this repo is

An attempt to run a company mostly through AI agents, with GitHub as the
system of record. Full mission/vision/phase: `docs/current/PROJECT.md`.
Current phase/milestone/active issue/blockers: `docs/current/STATE.md`. Read
these two when you need current status — don't reload them reflexively on
every turn.

Real product surfaces live under `app/products/` (kabukicho_survival_map_mvp,
minimal_launch_brief_generator, repository_operational_summary) and
`app/tools/approval_console_mvp`. Everything else under `system/`, `docs/`,
`basis/`, `adr/`, `specs/`, `contracts/` is process/governance scaffolding
that grew to a much larger footprint than the product code (roughly 800
markdown files and 24k lines of Python governing themselves — self-test,
drift detection, boundary validation, continuous governance, knowledge graph,
agent orchestrator, worker registry, queue/execution kernel, etc.). Be
skeptical of adding to this layer; prefer shrinking it when you touch it.

## Operating model

- Claude now covers both what ChatGPT (architecture, review, optimization)
  and Codex (implementation, refactoring, testing, PR) used to do separately.
- Human keeps: strategy, approval, capital allocation. Nothing merges to
  `main` without human review via PR.
- `basis/*.md` (policy corpus) and `adr/*.md` (decision records) are the real
  historical record of *why* things are the way they are. Read the relevant
  ones when a change touches that area — don't front-load all of them.
  `basis/` has an index at [basis/README.md](basis/README.md); some entries
  there are marked "stub" — those are unwritten placeholders, not adopted
  policy.

## Hard rules (technically enforced, not just documented)

- Never push directly to `main`. Always: feature branch → commit → push →
  PR → human review/merge. Activate the local guard once with
  `bash system/scripts/git/install_hooks.sh` (see
  `docs/current/MAIN_PROTECTION_POLICY.md`,
  `docs/current/BRANCH_AND_PR_OPERATING_PROCEDURE.md`).
- If a change affects architecture, governance, responsibility boundaries,
  workflow, data model, or runtime behavior, add or update an ADR under
  `adr/`.
- Before adding a new doc/script/workflow, check whether an equivalent
  artifact already exists (`basis/`, `adr/`, `docs/current/`, `system/`) and
  extend/fix it instead of creating a duplicate. This repo already has a
  duplication problem.
- Don't flatter or default to agreeing — if a design in this repo is
  overbuilt or inconsistent, say so directly.

## Validation

- Tests: `python -m pytest -q`
- Full repo self-validation: `python system/scripts/validate_all.py`
- Combined status export (what CI's `validate-all.yml` effectively checks):
  `bash system/scripts/check_repo_os_status.sh`

Run these before opening a PR for anything under `system/` or `app/`.
