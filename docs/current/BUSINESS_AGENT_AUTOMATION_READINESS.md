# BUSINESS_AGENT_AUTOMATION_READINESS

## Summary
Foundation for eventual full automation of the multi-business agent platform (`docs/current/PROJECT.md`'s AI-native-company goal). What's automatic today is only the *proposal* of the next task. Every execution still requires a human to explicitly approve that specific scope, every time — this doc does not change that.

## Capability Levels

### Level 0 (existing before this change)
Fully manual: a human runs `system/scripts/business_agent/propose_task.py` for every task, then approves it via the Approval Console, then triggers execution.

### Level 1 (this build — operational)
Event-driven queue population: when a `claude_invocation` or `data_fetch` role's execution succeeds, `system/core/business_agent_trigger.py::evaluate_and_enqueue_next_tasks()` automatically enqueues the role's configured `next_roles` (`system/core/agent_role_registry.py`'s `AgentRoleRecord.next_roles`) as new candidates in `system/runtime/business_agent_tasks/queue.json`, tagged `"source": "auto_trigger"`.

Seed chain (deliberately conservative, not exhaustive fan-out):
- `market_research` → `marketing`
- `marketing` → `doc_creation`
- `analytics` → `pdca`
- `pdca` → `market_research` (Level 2 — see below; terminal at Level 1)

At Level 1, a newly-enqueued task was also activated (made the current shared `agent_handoff/latest.json` scope) *unless* doing so would clobber a different scope that was currently approved and not yet executed. Level 2 (below) removes this shared slot and the guard along with it — every enqueued task is now activated unconditionally, since there is nothing left to clobber. Nothing at either level ever writes `approval.json` or invokes execution.

### Level 2 (operational) — per-task handoff scoping, concurrent chains, still fully human-approved
Goal: multiple businesses' chains — and multiple chains *within* one business (e.g. its PDCA loop and its content chain both progressing) — can progress simultaneously without one clobbering another. See `adr/ADR-0034-business-agent-per-task-handoff-scoping-level2.md`.

1. **Per-task handoff/approval scoping.** Each `(business_id, role_id, task_id)` gets its own handoff/approval files under `system/runtime/agent_handoff/scopes/{business_id}/{role_id}/{task_id}/`, mirroring the existing per-task artifact convention. The top-level `agent_handoff/latest.json`/`approval.json` remain exclusively for the pre-existing issue/draft repo-dev path. `system/core/business_agent_trigger.py`'s anti-clobber guard is deleted, not adjusted — two different scopes never share a path, so there's nothing left to clobber.
2. **File locking.** New `system/core/file_lock.py` (`fcntl.flock`, short timeout, hard error on timeout), applied only to the two files still genuinely shared across all businesses: `business_agent_task_queue.py`'s `queue.json` and `kpi_store.py`'s `kpi.json`. Per-task files need no locking.
3. **Approval Console updated** so each simultaneously-pending `business_role_task` candidate reports its own, independent `approval_status`/`execution_allowed`/`latest_execution_status` — previously all candidates shared one (stale, misleading) read.
4. **Execution concurrency**: `ApprovedAutonomousExecution.run()` and `run_approved_autonomous_execution.py` take optional `business_id`/`role_id`/`task_id` (all-or-nothing), so a human can safely run this in two terminals for two different scopes at the same time. A batch/multi-execute runner (one command running N approved scopes as parallel subprocesses) remains a stretch goal, not built here.
5. **PDCA loop closed**: `pdca → market_research` is now a real `next_roles` edge — safe now that a business's own PDCA-originated proposal and its in-flight content-chain proposal never share a slot.
6. **Release gate, verified**: a cross-scope forgery/leak test (approving scope A's approval must never authorize executing scope B), an issue/draft-path regression test, a two-business execute-independently test, and a same-business PDCA-loop-and-content-chain-coexist test. All pass; see `system/tests/test_agent_execution_approval.py`, `test_approved_autonomous_execution.py`, `test_business_agent_trigger.py`.
7. **Kill switch.** New `system/core/business_agent_automation_control.py` (`pause_automation`/`resume_automation`/`is_automation_paused`, backed by a sentinel file at `system/runtime/business_agent_tasks/automation_paused.json`) and CLI wrappers `system/scripts/business_agent/{pause,resume}_automation.py`. `business_agent_trigger.py::evaluate_and_enqueue_next_tasks()` checks this first and returns immediately (no enqueue, no activation) while paused. Scoped deliberately narrowly: pausing freezes *automatic* next-task proposal only — a human can still manually run `propose_task.py` / `set_execution_approval.py` / `run_approved_autonomous_execution.py` while paused, since an explicit human action should never be blocked by a safety control meant to stop *unattended* chaining. The Approval Console's `render_status()` surfaces an `AUTOMATION PAUSED` banner (reason/who/when) whenever the sentinel is present.

**Known limitations, deliberately not solved here**: no actual parallel/batch execution runner (two terminals, not one command); `queue.json`/`kpi.json` still serialize behind `flock` (rare in practice — human-driven CLI usage, not a hot loop).

### Level 3 (future, explicitly **not enabled**) — reducing/removing human approval
Forbidden without a new ADR and its own release gate per `docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md`'s prohibition: *"No new autonomy layer may be enabled unless a new readiness artifact and release gate are added first."* This is the one stage that crosses the line `docs/current/AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT.md` and `CLAUDE.md` ("Human keeps: strategy, approval, capital allocation") both draw explicitly — treat each sub-stage below as its own deliberate decision requiring explicit operator sign-off before design work starts, not something to slide into incrementally.

- **3a. Policy-based pre-approval** (the least risky first step, recommended entry point). A human authors a standing, revocable policy artifact (e.g. `system/runtime/agent_handoff/auto_approval_policy.json`) naming exactly which `(business_id, role_id)` pairs may be auto-approved, restricted to `claude_invocation`/`data_fetch` roles only (never `pluggable_provider`, which costs real money) and capped (e.g. max N auto-approvals per business per day). The system checks this policy instead of waiting for a fresh per-task approval — meaningfully different from "no approval": it's approval delegated in advance, by policy, revocable at any time, not approval removed.
- **3b. Scheduled/unattended execution.** Only after 3a exists: a scheduler (cron entry or a lightweight local daemon) periodically executes policy-eligible approved candidates without a human present. Requires: a real kill switch, an actual notification of what ran and its outcome (this doc's "runtime state is git-tracked" backstop is not a substitute for a human being told), a rollback plan, and a cost/budget guard — especially once Stage 4's paid `pluggable_provider` roles (image/video generation) are wired in, where a runaway loop costs real money, not just tokens.
- **3c. Publishing/distribution automation (this build — operational, publishing only, dry-run only).** Built directly on operator request (2026-07-10, two rounds of explicit sign-off), ahead of 3a/3b for content-generation execution (which remain unbuilt — this does not change how generation gets approved, only what happens to already-approved-and-executed drafts). See `adr/ADR-0035-business-agent-level-3c-policy-based-unattended-publishing.md` for full reasoning.
  - `system/runtime/publishing/policy.json` (hand-authored, PR-reviewed, absent by default — fail closed) authorizes a `(business_id, platform)` pair: allowed source roles (`marketing`/`doc_creation` only), daily/weekly caps, an affiliate-disclosure-tag requirement. Validated by `system/core/publishing_policy.py`.
  - A human runs `system/scripts/publishing/finalize_content.py` after a task has executed successfully, distilling its (often multi-option) raw output into the one exact string that may post. This artifact — not execution approval alone — is the sole eligibility signal; an approved-and-executed task with no finalized content is never published.
  - `system/scripts/publishing/run_scheduled_publish.py` finds all finalized-content candidates, checks policy/caps/dedup/both kill switches/content-integrity (a hash comparison blocks publishing if the underlying execution artifact changed since finalization)/disclosure-tag, and publishes eligible ones via `system/scripts/publishing/providers.py` (dry-run only — no platform credentials exist yet for X/Threads/note.com).
  - A second, dedicated kill switch (`system/core/publishing_control.py`, `pause_publishing.py`/`resume_publishing.py`) exists alongside the Level 1/2 one; the scheduler stops if *either* is engaged. Neither switch has a manual-override/force path.
  - Publishing state (dedup + counters) is sharded per `(business_id, platform)`, not one shared file, per the same reasoning ADR-0034 already established for per-task state.
  - Audit trail (`system/runtime/publishing/audit/`) surfaced in the Approval Console via a new banner.
  - **Known limitation, deliberately not solved here**: no real OS-level cron/launchd/daemon trigger — the scheduler is a fully-tested, manually-invokable script only. No real provider exists for any platform. No cross-role dedup across a single content thread (e.g. `marketing` and `doc_creation` both finalized for the same platform can both publish).

**Recommended sequencing**: ~~Level 2 (parallel, still human-approved)~~ done → ~~Level 3c (publishing, dry-run only)~~ done, ahead of sequence by explicit operator request → Level 3a (policy pre-approval for content generation, narrowly scoped) → Level 3b (scheduled execution under that policy) remain not built. Do not start further Level 3 work of any kind without the operator explicitly asking for that specific sub-stage.

## Verified Example
- Level 1: `text_syndicate/market_research/task-0001` (real, evidence-grounded output) → auto-enqueued and activated `text_syndicate/marketing/auto-0001`, which itself ran for real and produced a genuine marketing draft.
- Level 2: ran the trigger for real against production data — `text_syndicate/pdca` and `text_syndicate/market_research`'s content chain both had independently-pending, independently-tracked scopes for the same business at once, with no interference (see `test_business_agent_trigger.py::test_pdca_loop_and_content_chain_coexist_for_same_business`); a cross-scope forgery test confirms approving one business's scope can never authorize executing a different one.
- Kill switch: ran `pause_automation.py` against production, confirmed the console shows the `AUTOMATION PAUSED` banner and the trigger returns `[]` untouched, then ran `propose_task.py` manually while still paused and confirmed it still worked, then `resume_automation.py` and confirmed clean resumption with no trace left behind.
- Command sequence: unchanged from Level 0/1 for a single scope — `propose_task.py` (or an auto-triggered enqueue) → `set_execution_approval.py` (human) → `run_approved_autonomous_execution.py`, now with optional `--business-id`/`--role-id`/`--task-id` to target a specific scope.

## Forbidden Now
- No real OS-level cron/launchd entry or persistent daemon installed anywhere, for anything, including the new Level 3c publishing scheduler (`system/scripts/publishing/run_scheduled_publish.py` may exist and be run manually; actually wiring it to a recurring trigger is a separate, later, explicit ask — it would run outside this repo's git-tracked safety net).
- No GitHub Actions or other CI wiring into this flow.
- No removing or bypassing the human approval gate for content *generation* (`docs/current/AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT.md`) — Level 3c only ever acts on drafts a human already separately approved-and-executed through that gate.
- No real publishing provider (X/Threads/note.com) goes live before the operator independently obtains and wires real credentials — `dry_run` is the only provider today.
- No generalizing Level 3c's policy-based pre-authorization to `pluggable_provider` roles (image/video generation) — untouched, still forbidden.
- No GitHub mutation beyond the existing bounded approved flow.

**Runtime state here is git-tracked**, and this is itself a second, independent safety backstop beyond the approval gate at every level: even a successful auto-trigger chain link that gets activated only becomes durable/visible on `main` once a human reviews and merges the PR carrying that runtime-state change. It is not "live" the moment the script runs.
