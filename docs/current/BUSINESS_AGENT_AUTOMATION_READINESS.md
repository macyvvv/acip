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

### Level 2 (future, not built)
Full-cycle loop closure (`pdca → market_research`), a queue that supports more than one simultaneously-active handoff (removing the current single-canonical-slot constraint), concurrency-safe queue writes (today's `add_task`/`mark_task_status` do read-modify-write with no file locking — safe only because everything runs as a single local process today).

### Level 3 (future, explicitly **not enabled**)
Removing the human-approval requirement from execution. Forbidden without a new ADR and its own release gate, per `docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md`'s prohibition: *"No new autonomy layer may be enabled unless a new readiness artifact and release gate are added first."*

## Verified Example
- Business/role chain: `text_syndicate/market_research/task-0001` (real, evidence-grounded output) → auto-enqueued and activated `text_syndicate/marketing/auto-0001`.
- Command sequence: unchanged from Level 0 — `propose_task.py` (or an auto-triggered enqueue) → `set_execution_approval.py` (human) → `run_approved_autonomous_execution.py`.

## Forbidden Now
- No schedule/cron trigger.
- No GitHub Actions or other CI wiring into this flow.
- No removing or bypassing the human approval gate (`docs/current/AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT.md`).
- No daemonization.
- No GitHub mutation beyond the existing bounded approved flow.

## Known Limitations (not solved at Level 1, by design)
- **Single active handoff slot**: only one scope can be "the" currently-approvable candidate at a time (`system/runtime/agent_handoff/latest.json`). The anti-clobber guard prevents auto-trigger from silently overwriting an approved-and-pending scope, but two independent chains completing close together can still mean the second only enqueues rather than activates. Resolving this (multiple simultaneously-active handoffs) is Level 2.
- **No file locking anywhere in this codebase.** `business_agent_task_queue.py`'s read-modify-write operations assume a single local process. Fine today; would need addressing before any concurrent/multi-process execution.
- **Runtime state here is git-tracked**, and this is itself a second, independent safety backstop beyond the approval gate: even a successful auto-trigger chain link that gets activated only becomes durable/visible on `main` once a human reviews and merges the PR carrying that runtime-state change. It is not "live" the moment the script runs.
