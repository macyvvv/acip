# ADR-0037: Governance Layer Overhaul

## Status

Accepted

## Triggering Incident

`platform/app/products/kabukicho_survival_map/requirements.md` stated "no external
API dependency" as an absolute non-functional requirement. The operator
confirmed directly that the real underlying intent was narrower: avoid
unnecessary cost, start small — not a permanent architectural ban. Because
the rule was written as an unqualified absolute instead of naming the real
concern, it went stale and silently contradicted a later real product
decision (adding a paid Google Maps JavaScript API to the same product,
same session). Nothing forced that contradiction to surface until the
operator noticed the map's pin coordinates were low-quality estimates and
asked why they were never geocoded — the honest answer traced straight
back to the stale "no external API" rule.

Investigating that one incident surfaced a repo-wide pattern. The operator
then explicitly authorized a full governance-layer review:

> 根本的な問題があることがわかりました。Chatgptの指示は硬すぎます。claudeが動きやすく成るように、既存のポリシーは破壊していいです。その代わり、claudeにとって安全かつ効率的でロバストなポリシーに書き換えて下さい。

(“I've realized there's a fundamental problem. ChatGPT's instructions are
too rigid. It's okay to destroy the existing policy so Claude can work
more easily. Instead, rewrite it into a policy that is safe, efficient,
and robust for Claude.”)

Scope was confirmed via follow-up as the entire governance layer —
`platform/basis/`, `platform/adr/`, Level 3a auto-approval, `CLAUDE.md` hard rules, including
branch-protection/PR-required safety devices, all open for
reconsideration. A separate clarification narrowed the *reasoning* (not
the scope): the real lesson wasn't "external APIs are bad," it was "name
the actual concern (cost, here) instead of writing an absolute that loses
that nuance."

## Current Design (superseded)

This repository was originally operated by ChatGPT (architecture/review)
+ Codex (implementation), coordinating entirely through GitHub-committed
state because neither tool held conversation memory across sessions. That
produced a large written-contract layer: a 46-file `platform/basis/` policy corpus,
a 92-file-numbered aspiration index (many never authored past a stub), a
second, smaller ChatGPT↔Codex message/turn/thread simulation layer that
survived an earlier big cleanup (ADR-0032/PR#51), duplicate/dead CI
workflows and self-test scripts, and several `platform/docs/current/*.md` "current
state" documents frozen at an earlier phase that were never reconciled
against later real decisions.

Three parallel research passes (what's actually enforced vs. merely
descriptive; what ChatGPT/Codex-era scaffolding is still dead weight;
which rules are rigid absolutes that lost their real nuance) found:

- Most of `platform/basis/`'s 46 files were pure prose with zero enforcing code.
- A second ChatGPT↔Codex coordination layer
  (`platform/system/core/agent_{message_contract,state_manager,turn_runner,
  thread_runner,issue_bridge}.py`) survived ADR-0032's cleanup, still
  hardcoded `sender: ChatGPT, receiver: Codex`, and generated literal
  placeholder text. **Correction to ADR-0032's own record**: that ADR
  described `agent_issue_bridge.py` as part of "the real issue pipeline"
  (`agent_issue_bridge.py → local_execution_adapter.py`). This review's
  research found the opposite — git history shows only one commit ever
  touched those 5 files, and no workflow calls them. Whether ADR-0032 was
  inaccurate when written or the design was never completed as described
  is not resolved here; noted honestly rather than silently corrected.
- Two CI workflows (`continuous-governance.yml`, `repository-selftest.yml`)
  were empty stubs (`workflow_dispatch` only, no `jobs:`). A third
  (`repository-selftest-complete.yml`) was a byte-for-byte duplicate of
  `repository-semantic-selftest-v2.yml` under a different name. 8 of 9
  `platform/system/platform/scripts/selftest/` v1 scripts were unwired dead code,
  independently reimplemented (with independently drifting bugs — see
  Benefits) by the live `selftest_v2/semantic_checks.py`.
- `platform/docs/current/STATE.md` and `PROJECT.md` were dated 2026-06-22 and
  described "Phase 0/Phase 1," internally inconsistent with each other,
  and both retained a ChatGPT/Codex actor-responsibility split that
  `CLAUDE.md`'s own "Operating model" section already said was superseded.
  `platform/docs/current/MAIN_PROTECTION_POLICY.md` falsely claimed GitHub-side
  branch protection was configured; it is not, and is not available on
  this repo's plan (private, free tier).
- The identical unqualified "no external API calls" rule (the triggering
  pattern) recurred, unresolved, in two sibling products
  (`kabukicho_survival_map_mvp`, `minimal_launch_brief_generator`), plus
  an ambiguous "avoid external services" in a third
  (`repository_operational_summary`) that turned out, on reading the
  actual code, to really be about determinism, not cost.

## Proposed Design (adopted)

Staged across six independently-reviewed PRs, safest/most-mechanical
first:

1. **Removed confirmed-dead ChatGPT/Codex scaffolding** (PR #84): the
   second coordination-simulation layer and its tests, two EP
   completion-checklist scripts that only asserted the layer's own
   existence (deleted together with it, since `validate_all.py`
   auto-discovers and runs them), stale docs describing this exact
   retired feature, already-unreferenced Codex-role stub platform/docs/prompts/
   queue specs. Verified `platform/app/tools/approval_console_mvp/service.py`'s
   real, separate dependency on the *old* `agent_execution_approval.py`
   gate functions before touching anything near them — kept untouched.
2. **CI/self-test de-duplication** (PR #85, explicit operator sign-off
   obtained separately since it touched CI infrastructure directly): 2
   empty-stub workflows, 1 duplicate workflow, 1 duplicate wrapper script
   found during execution and folded in, 8 dead v1 selftest scripts.
   Chosen specifically because this is the exact duplicate-implementation
   pattern that had already caused a real bug earlier in the same
   session: two independently-drifting copies of the same
   secret-boundary regex, one of them (the unwired one) silently *not*
   fixing the CI failure it was believed to fix.
3. **Fixed the triggering pattern everywhere it recurred** (PR #86):
   rewrote the two sibling products' "no external API calls" and the
   third product's "avoid external services" (confirmed via direct code
   read: no network calls anywhere in that product, so the real concern
   is determinism) to name the real concern instead of a bare ban.
   Rewrote `BUSINESS_AGENT_AUTOMATION_READINESS.md`'s "Forbidden Now"
   section the same way, except the one item that really is a permanent
   absolute (no bypassing the human approval gate).
4. **Rewrote stale live-status docs** (PR #87): `STATE.md`, `PROJECT.md`,
   `ROOT_ALLOWLIST.md`, `ISSUE_OPERATOR_QUICKSTART.md`,
   `AUTONOMOUS_EXECUTION_READY.md`, root `README.md`,
   `MAIN_PROTECTION_POLICY.md`. Verified every path/script named in every
   rewritten doc actually exists before finalizing wording. Flagged,
   without fixing (out of scope for this pass): ~18 additional root-level
   "repository operating system" prose directories (`platform/baseline/`, `cache/`,
   `platform/packs/`, `registry/`, `rules/`, `runbooks/`, etc.) that look like more
   of the same mostly-unenforced pattern `platform/basis/` turned out to be.
5. **Consolidated `platform/basis/`'s 46-file corpus** (PR #88, explicit content
   review requested and given before merge, not just CI-green): added
   `platform/basis/CORE_PRINCIPLES.md` (9 principles, each traced to real enforced
   code or a genuinely durable concern), kept 2 files standalone,
   archived the remaining 43 to `archive/basis_corpus_2026/` with a
   mapping README, following the existing `archive/basis_skeleton/`
   precedent. Found and fixed two real, live dependencies on the moved
   file paths in the same pass (`semantic_checks.py`'s `REQUIRED_FILES`,
   wired into CI on every PR; `validate_baseline.py`, confirmed unwired
   but would have been a newly-dead reference).
6. **This ADR** (PR to follow), recording the above and what explicitly
   did not change.

## What Explicitly Did Not Change

- Level 3a's real pre-approval code
  (`platform/system/core/execution_pre_approval_{policy,state,control}.py`) and
  its live per-`(business_id, role_id)` daily caps in
  `platform/system/runtime/agent_handoff/auto_approval_policy.json` — genuinely
  enforced, untouched.
- Level 3c's policy-based unattended publishing (ADR-0035) — same
  reasoning, untouched.
- The PR-based git workflow itself, and the local pre-push hook
  (`platform/system/platform/scripts/git/prevent_main_push.sh`) that enforces it — the
  *documentation* of this (`MAIN_PROTECTION_POLICY.md`) was corrected to
  stop overclaiming GitHub-side enforcement that doesn't exist; the
  mechanism and the requirement itself are unchanged.
- The human-approval-gate contract
  (`platform/docs/current/AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT.md`) — confirmed
  already well-calibrated before this review even started; not rewritten.
- Secret-handling discipline — if anything, reinforced: the real,
  working `.env` → gitignored-local-config pattern built this same
  session (`platform/app/products/kabukicho_survival_map/build.py`'s
  `_write_local_gmaps_config()`) is now `CORE_PRINCIPLES.md` §5's cited
  example.
- `AGENTS.md` / `platform/.platform/system/{BOOT,REVIEW,STYLE,GLOSSARY}.md` as exempt
  historical record, per `CLAUDE.md`'s own existing carve-out — not
  touched by any stage.
- `platform/system/orchestrator/local_execution_adapter.py` — confirmed live
  (drives `claude -p` per ADR-0032), explicitly excluded from Stage 1's
  otherwise-adjacent deletions.
- `platform/contracts/AGENT_COMPLETION_CONTRACT.md` and the
  `completion_protocol.py` cluster it connects to — flagged during Stage
  1's research as needing its own separate investigation before any
  deletion decision; deliberately left alone, not a silent omission.

## Reason for Change

An absolute rule ("no X") that is really a stand-in for a narrower concern
(cost, irreversibility, determinism, secrets) reads as permanent even when
its real premise was contextual. Nothing forces it to be revisited when
circumstances change, so it silently goes stale — exactly what happened to
the triggering incident. The same failure shape, at a structural level,
also explains why this repo accumulated 46 files of policy prose with
almost no enforcing code behind it: each addition felt like "documenting a
rule," but nothing ever came back to ask whether the rule still matched
reality, or whether it was ever enforced in the first place. Two additional,
independent instances of stale/duplicated state were found and fixed as a
direct side effect of doing this review carefully (see Benefits) —
reinforcing that this wasn't a one-off, isolated incident.

## Benefits

- The triggering contradiction (and its two unresolved sibling instances)
  is fixed at the pattern level, not just the one reported case, with a
  new, explicit authoring convention (`CORE_PRINCIPLES.md` §9) to reduce
  recurrence going forward.
- 43 files of mostly-unenforced policy prose replaced by 9 principles that
  each name real, checkable, present-tense justification.
- Two real bugs found and fixed as a direct side effect, both examples of
  the same "unreconciled duplicate" pattern this review targeted: (a) a
  duplicate CI workflow silently running the same check twice under
  different names, discovered while removing dead self-test scripts; (b)
  `semantic_checks.py`'s hardcoded required-file list, which would have
  started failing on every PR the moment the `platform/basis/` files it named were
  moved, caught and fixed before it ever reached CI.
- A second ChatGPT↔Codex coordination-simulation layer, missed by
  ADR-0032's earlier, larger cleanup, is now actually gone.
- Live-status docs (`STATE.md`, `PROJECT.md`, root `README.md`) describe
  the repository Claude Code actually operates today, not a frozen
  snapshot from an earlier phase.

## Drawbacks

- `platform/basis/`'s original 46 files are no longer directly browsable as a flat
  list — a reader now needs to know to check `archive/basis_corpus_2026/`
  for anything not covered by the 9 compact principles. Mitigated by a
  full file-by-file mapping table in that archive's README.
- The ~18 additional root-level "repository operating system" prose
  directories found during Stage 4 (`platform/baseline/`, `cache/`, `platform/packs/`,
  `registry/`, `rules/`, `runbooks/`, etc.) were deliberately not audited
  or touched — this review's scope was `platform/basis/` plus the specific dead
  ChatGPT/Codex artifacts found, not a full sweep of every governance-
  adjacent root directory. A real, larger follow-up candidate, named
  explicitly rather than silently left for someone to rediscover.
- `platform/contracts/AGENT_COMPLETION_CONTRACT.md`'s cluster
  (`completion_protocol.py` and its dependents) was flagged as needing
  investigation but not investigated — deliberately deferred, not
  resolved.
- Two `platform/docs/platform/packs/README_*.md` files retain broken `platform/basis/019-026`
  references; four of the five were already broken before this review
  (per `platform/basis/README.md`'s own prior note that 001-025 were "lost at some
  point, not reconstructed"); the fifth (026) is newly broken by this
  review's move and was not fixed, since fixing it consistently would
  require reconstructing already-lost content this review didn't
  originate.
- Whether ADR-0032's description of `agent_issue_bridge.py` as live was
  ever accurate is unresolved (see Current Design section) — flagged, not
  chased down further.

## Impact Scope

- Deleted (Stage 1): 5 ChatGPT/Codex simulation-layer core files, 3 CLI
  scripts, 10 tests (including one found live during execution,
  `test_agent_handoff_automation_pack.py`), 2 EP checklist scripts + specs,
  ~20 stale/dead docs and stub files.
- Deleted (Stage 2): 3 CI workflows, 10 dead/duplicate Python scripts.
- Rewritten (Stage 3): 4 docs (3 product `requirements.md` + 1
  automation-readiness doc's "Forbidden Now" section).
- Rewritten (Stage 4): 7 docs.
- Moved (Stage 5): 43 `platform/basis/` files → `archive/basis_corpus_2026/`; added
  2 new files (`CORE_PRINCIPLES.md`, the archive's mapping `README.md`);
  rewrote `platform/basis/README.md`; fixed 2 live-code file-path dependencies and
  1 cross-referencing archive README.
- Unaffected: everything listed under "What Explicitly Did Not Change"
  above, plus all product code outside the touched `requirements.md`
  files, all of `platform/system/orchestrator/` except the deleted simulation-layer
  members, all of `platform/app/`.

## Migration Cost

Low. Each stage independently verified via `python -m pytest -q` and
`python platform/system/platform/scripts/validate_all.py` before its PR was opened; Stage 2
additionally verified against real CI (not just local) since it touched
`.github/workflows/*` directly; Stage 5 additionally verified its
required-file-list fix against a direct run of
`validate_semantic_selftest.py`. All six stages merged clean.

## Recommendation

Accepted and complete. Future governance additions should default to
`CORE_PRINCIPLES.md` §9's convention (name the real concern) and
`CLAUDE.md`'s existing duplication check (search for an existing
equivalent before adding a new doc/script/workflow) — both are now backed
by two concrete, in-repo examples of what goes wrong when they're skipped.

## Addendum (2026-07-14): platform/system/runtime/workers/ and governor/ archived

A repo-wide "is our current process/refactoring debt fine as-is"
consultation (all 15 acip subagents + `opsboard`'s synthesis) surfaced
`platform/system/runtime/workers/` and `platform/system/runtime/governor/` as more of the
same pattern this ADR already addressed for `platform/basis/` and the 18
root-level directories (`archive/root_scaffolding_2026/`) — confirmed via
the same test (`git grep` across `*.py`/`*.yml`/`platform/docs/`/`platform/system/`/`platform/app/`:
zero references to either path). Archived to
`archive/runtime_scaffolding_2026/` with the same per-directory rationale
format; `platform/docs/current/GOVERNOR_RECOMMENDATION_SSOT.md` updated to stop
describing a mechanism that was never actually wired up. Recorded here
rather than as a new ADR since it's the identical pattern and criterion
already adopted above, not a new decision.
