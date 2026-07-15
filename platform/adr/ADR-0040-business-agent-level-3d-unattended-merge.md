# ADR-0040: Business Agent Platform -- Level 3d: Unattended Merge for Scheduled Execution

## Status

Accepted

## Naming Correction (added on review)

This capability is **Level 3d**, not a sub-feature of Level 3b. This
platform's Level-3 lettering convention is one letter per distinct
human-approval-boundary crossing: 3a = pre-approval of the execution
*decision*, 3b = the scheduled *trigger* that acts on that decision
unattended, 3c = pre-approval of *publishing*. This ADR crosses a fourth,
independent boundary -- unattended *landing to `main`* -- which this ADR's
own Drawbacks section already named as "the first time content reaches
main with zero human eyes," a bigger crossing than 3b's original scope
(generation only). Originally filed as an extension of 3b; relabeled 3d
after a full Level 1-3 MECE review found the original framing understated
what this ADR actually does and could read as if "Level 3b" always meant
"schedule + merge," which it did not before this ADR existed.

## Triggering Incident

ADR-0038 (Level 3b) deliberately drew one line it would not cross: "the
scheduler never merges its own PR." In practice this meant every generation
PR the scheduler opened sat waiting for a human or an active Claude session
to review and merge it -- and during this same session, that turned out to
matter more than expected. A live Level 3b wake (PR #113) was investigated
for a suspected false-success bug; while root-causing it, the investigator
(reading the wrong copy of the repo state -- see below) initially
misdiagnosed a real success as a fabricated one. Once that was corrected, a
second, real problem surfaced: because nothing had merged PR #113, a second
wake (PR #115) and a third (triggered while tracing the second, PR #116)
all independently re-claimed and re-executed the *same* three
already-succeeded scopes (`kabukicho_survival_map/marketing/auto-0005`,
`kabukicho_survival_map/doc_creation/auto-0005`,
`text_syndicate/marketing/auto-0003`), burning three real `claude -p`
invocations' worth of cost on work that had already genuinely completed.
`_land_via_pr`'s design -- commit the wake's own runtime-state writes to a
new branch, open a PR, then unconditionally `git checkout main` -- means
the *local working tree* reverts to whatever `main` last had, which is
exactly what caused the investigator's initial misdiagnosis: inspecting
local disk state after a wake shows stale, pre-wake content, not the
genuinely fresh content that landed on the PR's own branch. The real
generated content was correct; the operational picture (nothing was
draining the backlog because nothing was merging) was the actual defect.

The operator, informed of this trade-off directly (never-auto-merge means
backlog only drains as fast as PRs get merged; PRs pile up during exactly
the unattended windows launchd exists to cover), explicitly authorized
crossing ADR-0038's original line: "構いません。claudeを信頼します。ただし、
claudeがその信頼に応えるべき自己チェック体制を備えてください" (that's fine,
I trust Claude; but build the self-check regime Claude should live up to
that trust with).

## Current Design (superseded in part)

`run_scheduled_execution.py` opens a PR per wake and always leaves it for a
human or an active Claude Code session to merge (ADR-0038's "Rejected
Alternatives": "Auto-merging the scheduler's own PRs: rejected outright --
this is the one line this design will not cross"). This ADR revisits that
line under an explicit, informed operator go-ahead, and per this repo's own
established practice for every prior autonomy-expanding change (Level 1,
2, 3a, 3c, 3b): design -> one adversarial critique pass (via a forked
subagent, grounded in the actual code and ADR-0038's own Rejected
Alternatives) -> revise -> implement.

## Proposed Design (adopted)

`run_scheduled_execution.py` may merge its own opened PR unattended, only
when every one of the following gates passes. The first gate that fails
leaves the PR open for human/session review, exactly as before this ADR --
auto-merge is additive, never a replacement for the existing fallback.

1. **All-succeeded gate**: every scope executed in the wake reported
   `execution_result_status == "success"`. Any partial failure in the batch
   means no merge is attempted for any of it.
2. **Path-allowlist re-verification**: the actual committed diff
   (`git diff --name-only main...branch`) is re-checked against
   `_TRACKED_RUNTIME_PATHS`, not just trusted from the earlier `git add`
   step -- defense in depth against a future bug widening what gets staged.
3. **Local validation**: `python -m pytest -q` and
   `python platform/system/platform/scripts/validate_all.py` both clean on the wake's own
   branch.
4. **Stale-base check**: immediately before merging (not just at wake
   start), `origin/main` is re-fetched and compared against the base SHA
   recorded when the wake began. If `main` has advanced, the merge is
   aborted and the PR left open. This is the direct fix for the concurrency
   failure mode this same session hit for real (PR #115 vs. #116) -- and
   it is deliberately checked against GitHub's own remote state, not the
   local whole-invocation file lock (`platform/system/core/file_lock.py`), because
   that lock only protects one process on one clone; this repo has a
   confirmed second local clone, so a local-only lock cannot be the real
   safety property here.
5. **CI-green gate**: GitHub's own required checks (Boundary Validation,
   Repository Semantic SelfTest v2) are polled with a bounded timeout (5
   minutes, 15s interval) -- not green, or timeout, both leave the PR open.
   Never blocks/retries indefinitely.
6. **Merge kill switch**: a 5th independent switch
   (`platform/system/core/scheduled_merge_control.py::is_scheduled_merge_paused`),
   distinct from the existing four, gating only the merge step -- an
   operator can freeze auto-merge while leaving generation running, or vice
   versa.
7. **Circuit breaker**: `platform/system/core/scheduled_merge_circuit.py` counts
   *consecutive* merge-gate failures across wakes (any gate above, 2-5 --
   including a stale-base abort, which the critique pass flagged as the
   failure mode most likely to recur). 3 in a row auto-engages the merge
   kill switch (`paused_by="circuit_breaker"`) until a human/session clears
   it. A single success resets the counter.
8. **Identifier validation**: `business_id`/`role_id`/`task_id` are
   validated against `^[A-Za-z0-9_-]+$` in `find_scheduled_candidates`,
   before a wake even attempts execution -- once merge can land with zero
   human eyes on the diff, a malformed identifier reaching a filesystem
   path (e.g. via `propose_task.py`, which accepts arbitrary strings today)
   is a real path-traversal-shaped risk that used to be caught by PR
   review.
9. **Audit trail**: every merge attempt/skip and its reason is recorded in
   the existing `platform/system/runtime/scheduler/audit/` payload
   (`merge_attempted`, `merge_result`, `merge_skip_reason`).
10. **Rollback**: `platform/system/platform/scripts/business_agent/rollback_scheduled_merge.py`
    prepares a revert PR for a given merge commit -- itself never
    auto-merged, requiring the same human/session review a bad merge
    should have gotten in the first place.

Deliberately **not** built: a separate daily cap on auto-merges (the
existing per-role generation caps already bound cost/frequency; the
critique pass judged a merge-specific cap low-value complexity, addable
later if real data justifies it) and any machine-checkable validation
against `platform/contracts/roles/*_OUTPUT_CONTRACT.md` beyond what gate 1 already
guarantees (those contracts are prose quality standards -- "is this a
complete document, not an outline" -- not a mechanically checkable schema
today; claiming to validate them programmatically here would overclaim
what gate 1's `success` flag, hardened by PR #114's CLI-failure-notice
check, actually establishes).

## Reason for Change

Direct, informed operator authorization, given the concrete cost of the
status quo (redundant re-execution burning real API calls every wake until
a human/session happens to merge) and an explicit request for a
self-check regime commensurate with the trust extended. Designed via this
repo's own established pattern -- one adversarial critique pass via a
forked subagent, grounded in the actual code (`run_scheduled_execution.py`,
`scheduled_execution_control.py`) and ADR-0038's own Rejected Alternatives
section (to check whether this design actually closes those original
objections rather than papering over them) -- which found the stale-base
race as the most severe, concrete (not hypothetical) issue, confirmed by
the exact PR #115/#116 collision that happened in this same session.

## Benefits

- Directly closes the gap that caused real, observed waste this session:
  backlog stops requiring a human/session to notice and merge before it
  can progress.
- The stale-base check is cross-process-safe (checks GitHub's remote
  state), unlike the existing local file lock, which only ever protected
  one process on one clone.
- Every gate fails closed (leaves the PR open, this repo's existing
  fallback) rather than failing open.
- Adds zero new content-generation authorization surface -- the existing
  Level 3a policy/cap/eligibility machinery (ADR-0036) is unchanged; this
  ADR only adds a gate in front of an already-authorized action's landing
  step.

## Drawbacks

- This is the first change in this platform's history where content can
  reach `main` with zero human or interactive-Claude-session eyes on the
  diff before it lands. Every gate above is designed to bound the risk,
  not eliminate the fact that this line, once crossed, is crossed.
- The rollback story is no longer simply "don't merge" -- it now depends on
  `rollback_scheduled_merge.py` being run correctly after a bad merge is
  *noticed*, which still requires a human or session to notice it in the
  first place (this ADR does not add automated post-merge content review).
- CI-polling adds real wall-clock time to a wake (up to 5 minutes per
  merge attempt) and a new external dependency (GitHub Actions
  availability) on the unattended path.
- The circuit breaker's threshold (3) is a judgment call, not derived from
  data -- may need tuning once real unattended operation accumulates
  history.

## Rejected Alternatives

- **A separate daily cap on auto-merges**: rejected as low-value
  complexity given the existing per-role generation caps already bound
  the underlying cost/frequency -- addable later if real data justifies
  it.
- **Machine-validating each artifact against its `platform/contracts/roles/*_OUTPUT_
  CONTRACT.md`**: rejected as overclaiming -- those contracts are prose
  quality standards not mechanically checkable today; a future LLM-judge-
  based check is a legitimate separate project, not folded in here.
- **Relying on the existing local file lock as the concurrency safety
  property**: rejected -- confirmed insufficient, since this repo has (at
  least) two local clones and the lock is per-process/per-clone. The
  stale-base check against GitHub's own remote state is the real
  mitigant.
- **Auto-reverting a bad merge unattended**: rejected -- the situation that
  calls for a rollback is exactly the situation that calls for a human or
  active session looking at the diff before anything further lands, not
  another unattended action compounding the first one.

## Impact Scope

- New: `platform/system/core/scheduled_merge_control.py`,
  `platform/system/core/scheduled_merge_circuit.py`,
  `platform/system/platform/scripts/business_agent/{pause,resume,rollback}_scheduled_merge.py`,
  this ADR, `platform/system/tests/test_scheduled_merge_control.py`,
  `platform/system/tests/test_scheduled_merge_circuit.py`, new tests appended to
  `platform/system/tests/test_run_scheduled_execution.py`.
- Modified: `platform/system/platform/scripts/business_agent/run_scheduled_execution.py`
  (`_land_via_pr` extended to attempt merge; `find_scheduled_candidates`
  gains identifier validation; `ScheduledExecutionSummary`/audit payload
  gain merge fields), existing tests in `test_run_scheduled_execution.py`
  updated for `_land_via_pr`'s new 5-tuple return shape.
- Unaffected: Level 3a's policy/cap/eligibility machinery
  (`execution_pre_approval_policy.py`, `execution_pre_approval_state.py`),
  Level 3c publishing, the repo's never-push-to-`main` hard rule (every
  landing still goes through a PR; this ADR only changes who clicks
  merge), the human-approval requirement for any scope without a Level 3a
  policy.

## Migration Cost

Low. Ships with the merge kill switch unpaused by default (auto-merge is
live once this merges) but every other gate must independently pass for
any real merge to happen -- consistent with this repo's practice of
shipping a capability's mechanics and gates together rather than shipping
gates separately from what they gate.

## Recommendation

Accepted. Directly fixes an observed, real cost (redundant re-execution
from unmerged PRs) under explicit, informed operator authorization, with a
gate design that survived one adversarial critique pass grounded in the
actual code and this session's own concrete failure (PR #115/#116). The
one-time trust boundary crossing (content reaching `main` unattended) is
bounded by ten independent, fail-closed gates rather than removed
review entirely.

## Release-gate checklist

- [x] ADR-0040 written.
- [x] `pytest -q` and `validate_all.py` green (408 tests, up from 391).
- [x] At least one real wake with something to merge, observed end-to-end
      by the operator (gate-by-gate, not just the final outcome). PR #118
      (2026-07-14/15): 3 real scopes executed successfully, all gates
      passed (all-succeeded, allowlist, local validation, stale-base check
      against real `origin/main`, GitHub CI green), merged unattended.
      Content spot-checked as genuine (fresh `captured_at`, real generated
      marketing copy, `exit_code=0`, `success=True`). Backlog dropped from
      14 to 12 candidates.
- [x] Circuit breaker demoed tripping for real (3 consecutive induced
      failures) and clearing via `resume_scheduled_merge.py`. Confirmed
      `is_scheduled_merge_paused()` flips to `True` with
      `paused_by="circuit_breaker"` on the real production state path,
      then cleanly resumed.
- [x] `rollback_scheduled_merge.py` demoed against a real (deliberately
      bad, clearly-labeled throwaway) merge (PR #120 -> merge commit
      `0fae0fc`): the script correctly opened a revert PR (#121, diff
      confirmed it only deleted the throwaway file) and did NOT auto-merge
      it (`merged=false`) -- reviewed and merged manually, leaving no
      permanent trace.

Incidental finding while verifying: a pre-existing, unrelated flaky test
(`test_stale_claim_can_be_reclaimed`, a UTC day-boundary bug in the test
itself, not in `execution_pre_approval_state.py`) reproduced live during
this verification and was fixed in the same session (separate PR #122).
