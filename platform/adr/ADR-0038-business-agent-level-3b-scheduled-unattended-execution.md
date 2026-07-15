# ADR-0038: Business Agent Platform Level 3b — Scheduled/Unattended Execution

## Status

Accepted

## Current Design (superseded)

Level 3a (ADR-0036) let a written, capped, revocable policy pre-approve the execution
*decision* for a `business_role_task` scope, so a human no longer has to run
`set_execution_approval.py` for every generation task. But nothing actually *calls*
`run_approved_autonomous_execution.py` unless a human (or Claude, in an active session)
does so. `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md` named this gap
explicitly as "Level 3b, scheduled/unattended execution" and deliberately left it
unbuilt, listing four prerequisites: a real kill switch, an actual notification of
what ran (git-tracked state alone is not sufficient), a rollback plan, and a
cost/budget guard — plus, per `AUTONOMOUS_OPERATIONAL_BASELINE.md`, a new ADR and its
own release gate before any new autonomy layer may be enabled.

As of this ADR, this gap has real, live consequences: 13 `kabukicho_survival_map/
marketing` candidates sit stalled in `queue.json`, auto-triggered by Level 1 but never
executed because nobody has manually invoked the runner against each one — roughly 5
days' worth of backlog at the existing 3/day policy cap, growing.

## Proposed Design (adopted)

**Scope, per explicit operator instruction**: generation-only roles
(`market_research`, `marketing`, `doc_creation`, `scenario_writing`, and by extension
any future `claude_invocation`/`data_fetch` role) may run unattended, continuously.
Posting/publishing (Level 3c) and any deploy action remain human-gated, unchanged —
this ADR does not touch either.

- `platform/system/core/scheduled_execution_control.py` — a 4th independent kill switch
  (`is_scheduled_execution_paused`), distinct from `is_automation_paused` (Level 1/2
  proposal-freeze), `is_pre_approval_paused` (Level 3a policy-claim gate), and
  `is_publishing_paused` (Level 3c) — each switch's own docstring is a promise about
  what it does and does not affect; reusing one here would silently redefine it for a
  new caller, the same reasoning ADR-0036 already applied when it declined to reuse
  `is_automation_paused`.
- `platform/system/core/business_agent_task_queue.py::list_candidate_tasks()` — a new, pure,
  read-only selector (`queue.json` had none before this).
- `platform/system/platform/scripts/business_agent/run_scheduled_execution.py` — the runner. Checks the
  new switch first; takes a whole-invocation lock (`platform/system/core/file_lock.py`, short
  timeout, skip-and-log rather than block if a previous wake is still running);
  pre-filters candidates to one `task_id` per `(business_id, role_id)` pair (oldest
  first, capped at `MAX_TASK_EXECUTIONS_PER_WAKE = 5`) using
  `get_execution_pre_approval_policy()` — the *same* function
  `ApprovedAutonomousExecution.run()` itself calls, not a second, independently
  maintained eligibility check, so the pre-filter can never drift from what's
  actually authoritative; executes each via the existing
  `ApprovedAutonomousExecution(base_path).run(business_id=..., role_id=..., task_id=...)`
  — the exact call a human could make manually today, continuing past any single
  scope's failure; sets `CLAUDE_EXECUTION_TIMEOUT_SECONDS` explicitly in its own
  process environment (a launchd/cron-invoked process inherits no interactive shell's
  exported env vars — this already caused a real failure,
  `text_syndicate/market_research/task-0003-finance-saas-niche` timing out at the 60s
  default before this fix existed) rather than relying on inherited state.
- Notification: a local audit trail (`platform/system/runtime/scheduler/audit/`, gitignored —
  rewritten several times a day, not meant to be git history) plus, when a wake
  actually executed something, an auto-opened PR (branch → commit of the touched
  runtime-state paths → push → `gh pr create`). **The scheduler never merges its own
  PR** — this is the operator's own explicit, informed choice after being shown the
  tradeoff against a local-only or dedicated-branch-only alternative, made because
  local files alone are invisible until a session reopens. Merge stays exactly where
  the standing "マージも承認なく行って良い" authorization already put it: a human, or
  Claude in an active session, never an unattended process.
- Git safety: the landing step refuses to touch anything if the working tree isn't
  clean *before* the wake starts (protects a human's own in-progress, uncommitted work
  on the same clone from ever being partially committed by an unattended process), and
  always returns to `main` afterward regardless of outcome.
- Budget guard: the per-wake cap above, on top of the per-role
  `max_auto_approvals_per_day`/`week` caps Level 3a already enforces regardless of
  trigger source. **Named consequence, not just "the cap covers it"**: summing every
  currently-enabled policy's `max_auto_approvals_per_day` = 28 real `claude -p`
  invocations/day, guaranteed, once the scheduler runs often enough to hit every cap
  daily — a real change from today's sporadic, session-gated actual usage.
- Rollback: eligible roles are structurally read-only (`role_kind` in
  `{claude_invocation, data_fetch}`, no `Write/Edit/MultiEdit/Bash/NotebookEdit` in
  `allowed_tools`, re-verified live at claim time — unchanged from Level 3a) — nothing
  reaches `main` without a human/Claude-reviewed merge, so rollback is "don't merge"
  or `git revert`.
- Trigger mechanism, staged: the runner is a plain, manually-invokable script first,
  piloted via session-scoped `CronCreate` (cheap, reversible, exercises the real
  pipeline). Installing a persistent macOS `launchd` LaunchAgent — the only thing that
  survives a closed chat session — is a separate, later, explicit operator go-ahead,
  never bundled into this PR; it modifies the operator's machine outside the git repo,
  a materially bigger and less reversible step than a commit.

## Reason for Change

Direct operator request, mid-session: "今後も自動化させたい。claudeの手が空かない様に
したい" (keep this going forward; don't let Claude's hands sit idle), with an explicit
scope boundary drawn when pressed: generation work is fine unattended;
posting/deployment must stay human-gated. This maps exactly onto the Level 3b gap this
repo's own readiness doc had already named and deliberately deferred pending its four
stated prerequisites, which this ADR satisfies.

This design was produced via the same design → adversarial-critique cycle used for
every prior autonomy-expanding Level this session (1, 2, 3a, 3c): 2 research passes
fact-gathering the existing kill switches/claim state machine/readiness doc/live
backlog, 1 design pass, 1 adversarial critique pass. The critique found 2 blocking
issues (the overlapping-wake race and the timeout-env-inheritance gap, both folded
into the design above — the timeout gap was independently confirmed already live in
production data, not hypothetical) plus several worth-fixing items (the 28/day cost
line, the stale `text_syndicate/task-0003` queue status, a shared-helper requirement
for the pre-filter).

## Benefits

- Directly delivers the stated capability: generation work for any policied scope
  keeps moving without a human or Claude needing to be present to invoke each step.
- Costs zero new authorization surface — the runner can only ever do what a human
  could already do manually today via `run_approved_autonomous_execution.py`; Level
  3a's existing policy/cap/eligibility machinery is the sole authority, reused
  verbatim, not re-implemented.
- Fixes a real, pre-existing bug for free: the 60s default CLI timeout not surviving
  an unattended invocation — this was about to bite production regardless of whether
  Level 3b shipped, since it already had.
- The 13-item `kabukicho_survival_map/marketing` backlog, and any future backlog like
  it, now drains automatically at the existing policy cap instead of requiring manual
  attention.

## Drawbacks

- Guaranteed daily token/API cost increase (the 28/day figure above) — a real,
  ongoing consequence of turning occasional into scheduled, not just a theoretical
  ceiling.
- The scheduler auto-opening PRs is a genuinely new class of automated git action in
  this repo — every PR before this one was opened by a human or by Claude in an
  active, judgment-exercising session. The safety property (never merges, always
  reviewable, refuses a dirty tree) is designed to bound this, but it is a real
  precedent shift worth naming plainly rather than treating as "just more of the same
  PR flow."
- The `CronCreate` pilot stage is itself session-scoped (dies when this chat session
  ends, auto-expires after 7 days) — it does not yet deliver the literal "hands never
  idle even when nobody's talking to Claude" outcome; that requires the separate,
  later `launchd` go-ahead this ADR deliberately does not include.
- Local-audit-trail-plus-PR is not a push notification; the operator still has to
  either open a session or check GitHub to see what ran, unless/until a real
  notification channel is added later.

## Impact Scope

- New: `platform/system/core/scheduled_execution_control.py`,
  `platform/system/platform/scripts/business_agent/{pause,resume}_scheduled_execution.py`,
  `platform/system/platform/scripts/business_agent/run_scheduled_execution.py`, this ADR,
  `platform/system/tests/test_scheduled_execution_control.py`,
  `platform/system/tests/test_run_scheduled_execution.py`, `platform/system/runtime/scheduler/`
  (sentinel tracked, `audit/` gitignored).
- Modified (additive only): `platform/system/core/business_agent_task_queue.py`
  (`list_candidate_tasks`), `platform/system/tests/test_business_agent_task_queue.py`,
  `.gitignore`, `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`,
  `platform/docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md`.
- Unaffected: `ApprovedAutonomousExecution`, `execution_pre_approval_*.py`,
  `publishing_control.py`, `business_agent_automation_control.py`,
  `business_agent_trigger.py` — the runner is purely a new *caller* of the existing,
  unmodified Level 3a authorization path. Level 3c publishing, the repo's
  never-push-to-`main` hard rule, and the human-approval requirement itself are all
  completely untouched.

## Migration Cost

None. No existing state changes shape or location; the runner is additive, and the
13-item backlog it will start draining already exists in its current `queue.json`
shape, seeded by Level 1 before this ADR.

## Recommendation

Recommend. Satisfies all four prerequisites the readiness doc itself named before
this could be built, adds zero new authorization surface beyond what Level 3a already
grants, fixes a real pre-existing bug along the way, and keeps the two genuinely
risky action classes (publishing, deployment) exactly as human-gated as before. The
remaining step to the operator's literal "hands never idle" request — a persistent
`launchd` LaunchAgent — is deliberately deferred to its own separate, explicit
go-ahead per the release-gate checklist below, not because it's unsafe by design, but
because installing something that runs on the operator's machine independent of any
Claude Code session is a materially different kind of commitment than a git commit,
and deserves its own moment of explicit sign-off rather than being bundled in here.

## Rejected Alternatives

- **Reusing an existing kill switch** instead of a 4th dedicated one: rejected for the
  same reason ADR-0036 rejected reusing `is_automation_paused` for Level 3a — each
  switch's docstring is a load-bearing promise about what it does and does not affect,
  and conflating "should the unattended loop attempt anything this wake" with either
  "should new candidates be proposed" or "should this scope's policy currently
  authorize execution" would quietly redefine an existing contract for a new caller.
- **Auto-merging the scheduler's own PRs**: rejected outright — this is the one line
  this design will not cross. The standing merge-without-asking authorization was
  scoped to Claude, in an active session, merging PRs it opened; extending it to an
  unattended process merging its own work was never asked for and is not assumed
  here.
- **Local-audit-trail-only notification, no PR** (the design pass's original
  recommendation, citing the readiness doc's "no GitHub mutation beyond the existing
  bounded approved flow" line): rejected by the operator after being shown the
  tradeoff explicitly — invisible-until-next-session was judged worse than the
  precedent shift of an automated PR-open (never merge). This required narrowing the
  readiness doc's forbidden-list line, done explicitly here rather than silently.
- **Bundling the `launchd` LaunchAgent install into this same PR**: rejected — modifying
  the operator's machine outside the git repo is a materially bigger, harder-to-reverse
  step than shipping code, and gets its own later, explicit go-ahead per the release
  gate below.
- **A single "drain the whole backlog" run with no per-wake cap**: rejected — the
  13-item backlog alone would consume most of a day's combined cap allowance in one
  wake; `MAX_TASK_EXECUTIONS_PER_WAKE=5` bounds worst-case blast radius per invocation
  independent of how large a backlog grows.

## Release-gate checklist (per `AUTONOMOUS_OPERATIONAL_BASELINE.md`'s "new readiness
## artifact and release gate" requirement — gates the `launchd` install step
## specifically; code and the `CronCreate` pilot ship independently of this list)

- [x] ADR-0038 written.
- [ ] `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`'s Level 3b section updated
      with a real verified example (not a claim) and the 28/day cost line.
- [ ] Kill switch demoed pause/resume against production.
- [x] `pytest -q` and `validate_all.py` green, including the never-shells-out-to-git
      and no-drift tests.
- [ ] At least one real manual dry-run, plus several real `CronCreate`-piloted wakes,
      with audit-trail + opened-PR evidence reviewed by the operator.
- [ ] A rollback drill: intentionally let one piloted wake produce something to
      discard, confirm "don't merge" is sufficient in practice.
- [ ] A separate, explicit operator go-ahead naming `launchd` specifically.
