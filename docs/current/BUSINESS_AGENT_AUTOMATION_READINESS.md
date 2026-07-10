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
- everything else terminal (including `pdca` — closing the loop back to `market_research` is Level 2, not this stage)

A newly-enqueued task is also activated (made the current `agent_handoff/latest.json` scope, ready for a human to approve) *unless* doing so would clobber a different scope that is currently approved and not yet executed — in that case it stays enqueued-only, visible in `queue.json`, and can be activated later by re-proposing it. Nothing at Level 1 ever writes `approval.json` or invokes execution.

### Level 2 (future, not built) — concurrent / parallel chains, still fully human-approved
Goal: multiple businesses' chains can progress simultaneously without one clobbering another, and the full PDCA loop can close. Needs its own ADR (this is a real architecture change, not additive like Level 1) and its own release gate before starting.

1. **Multi-slot handoff.** Replace the single canonical `system/runtime/agent_handoff/latest.json` with a per-scope handoff (e.g. `system/runtime/agent_handoff/scopes/{business_id}__{role_id}__{task_id}.json`), so two businesses' pending approvals can coexist without one overwriting the other. This removes the need for Level 1's anti-clobber guard entirely rather than working around it.
2. **File locking.** `system/core/business_agent_task_queue.py` / `kpi_store.py` / `business_agent_handoff.py` currently do unlocked read-modify-write, safe only because everything runs as a single local process today. Add a lock (e.g. `fcntl.flock` with a timeout) around each read-modify-write cycle before any concurrent invocation is safe.
3. **Approval Console update** so a human can review and approve several simultaneously-pending candidates in one sitting without them interfering with each other, now that they don't share one slot.
4. **Execution concurrency.** Start with the simplest form: once (1)+(2) land, a human can safely run `run_approved_autonomous_execution.py` in two terminals for two different businesses at the same time — no new orchestration code needed, this "just works" once the clobbering/locking problems are gone. A batch/multi-execute runner (executing several approved scopes in parallel subprocesses from one command) is a stretch goal on top, not a prerequisite.
5. **Close the PDCA loop**: add `pdca → market_research` to `next_roles` (deliberately left terminal at Level 1 specifically because a continuous loop without multi-slot handoffs would spam the single slot every cycle).
6. **Release gate**: a concurrency test (two businesses' chains run through propose→approve→execute interleaved, verify no data loss or silent overwrite) and a documented pause/kill-switch (e.g. a sentinel file the trigger checks before enqueueing, so all chains can be frozen at once if something looks wrong).

### Level 3 (future, explicitly **not enabled**) — reducing/removing human approval
Forbidden without a new ADR and its own release gate per `docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md`'s prohibition: *"No new autonomy layer may be enabled unless a new readiness artifact and release gate are added first."* This is the one stage that crosses the line `docs/current/AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT.md` and `CLAUDE.md` ("Human keeps: strategy, approval, capital allocation") both draw explicitly — treat each sub-stage below as its own deliberate decision requiring explicit operator sign-off before design work starts, not something to slide into incrementally.

- **3a. Policy-based pre-approval** (the least risky first step, recommended entry point). A human authors a standing, revocable policy artifact (e.g. `system/runtime/agent_handoff/auto_approval_policy.json`) naming exactly which `(business_id, role_id)` pairs may be auto-approved, restricted to `claude_invocation`/`data_fetch` roles only (never `pluggable_provider`, which costs real money) and capped (e.g. max N auto-approvals per business per day). The system checks this policy instead of waiting for a fresh per-task approval — meaningfully different from "no approval": it's approval delegated in advance, by policy, revocable at any time, not approval removed.
- **3b. Scheduled/unattended execution.** Only after 3a exists: a scheduler (cron entry or a lightweight local daemon) periodically executes policy-eligible approved candidates without a human present. Requires: a real kill switch, an actual notification of what ran and its outcome (this doc's "runtime state is git-tracked" backstop is not a substitute for a human being told), a rollback plan, and a cost/budget guard — especially once Stage 4's paid `pluggable_provider` roles (image/video generation) are wired in, where a runaway loop costs real money, not just tokens.
- **3c. Publishing/distribution automation.** Separate from execution automation: every content-role contract today states `auto posting: prohibited`. Whether/how drafted content ever reaches Twitter/Threads/note.com is its own decision with real reputational/compliance exposure (the `text_syndicate` market_research findings already flagged a live compliance question — note.com's affiliate-disclosure rules). Recommend this be the *last* thing automated, not the first, and that it may reasonably stay permanently human-gated (a human copy-pastes the approved draft) even after 3a/3b exist for content generation.

**Recommended sequencing**: Level 2 (parallel, still human-approved) → Level 3a (policy pre-approval, narrowly scoped) → Level 3b (scheduled execution under that policy) → Level 3c (publishing, last, likely to stay partially manual regardless). Do not start Level 3 work of any kind without the operator explicitly asking for that specific sub-stage.

## Verified Example
- Business/role chain: `text_syndicate/market_research/task-0001` (real, evidence-grounded output) → auto-enqueued and activated `text_syndicate/marketing/auto-0001`.
- Command sequence: unchanged from Level 0 — `propose_task.py` (or an auto-triggered enqueue) → `set_execution_approval.py` (human) → `run_approved_autonomous_execution.py`.

## Forbidden Now
- No schedule/cron trigger.
- No GitHub Actions or other CI wiring into this flow.
- No removing or bypassing the human approval gate (`docs/current/AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT.md`).
- No daemonization.
- No GitHub mutation beyond the existing bounded approved flow.

## Known Limitations at Level 1 (addressed by Level 2, see above)
Single active handoff slot and no file locking — see Level 2's items 1-2.

**Runtime state here is git-tracked**, and this is itself a second, independent safety backstop beyond the approval gate at every level: even a successful auto-trigger chain link that gets activated only becomes durable/visible on `main` once a human reviews and merges the PR carrying that runtime-state change. It is not "live" the moment the script runs.
