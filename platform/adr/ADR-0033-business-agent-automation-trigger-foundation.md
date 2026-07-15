# ADR-0033: Business Agent Automation Trigger Foundation

## Status

Accepted

## Current Design (superseded)

The multi-business agent platform (ADR-adjacent work from PRs #54/#55/#56, no prior ADR filed for it) requires a human to manually run `platform/system/platform/scripts/business_agent/propose_task.py` for every single task, for every role, in every business — including the completely predictable follow-on step (e.g. proposing `marketing` after `market_research` finishes, or `pdca` after `analytics` finishes). The Approval Console already reports "N candidates; operator selection required" when multiple tasks are queued, but a pre-existing bug meant this was aspirational: `ApprovalConsoleService.load_scopes()` computed `handoff_id` for every `business_role_task` scope from whatever the *globally currently active* handoff's `request_id` was, not from that scope's own identity — so a queued-but-not-active candidate could never actually be approved; only the one scope already sitting in `agent_handoff/latest.json` was approvable at all.

## Proposed Design (adopted)

Two additive changes, both scoped to the business-agent path only:

1. **Fix the `handoff_id` bug**: `platform/system/core/business_agent_handoff.py` exposes `compute_request_id(business_id, role_id, task_id)` (previously private `_request_id`); the console's `business_role_task` loop now uses it to compute a scope-specific `handoff_id` instead of echoing the global current handoff. A human can now approve any queued candidate, active or not, ahead of time.
2. **Auto-propose the next task on success**: `AgentRoleRecord` gains a `next_roles: tuple[str, ...]` field (`market_research → marketing`, `marketing → doc_creation`, `analytics → pdca`, everything else terminal). A new plain-function module, `platform/system/core/business_agent_trigger.py::evaluate_and_enqueue_next_tasks()`, is called from `ApprovedAutonomousExecution._run_business_agent()` immediately after a *successful* execution (never on failure). It always enqueues the next task(s) into `platform/system/runtime/business_agent_tasks/queue.json` (tagged `source="auto_trigger"`), and activates it (writes `agent_handoff/latest.json`) *unless* doing so would clobber a different scope that is currently approved and not yet executed.

Nothing here writes `approval.json` or invokes execution. Every execution still requires a human to run `set_execution_approval.py` — unchanged, untouched.

## Reason for Change

The user explicitly asked for "the foundation for full automation," clarifying: (a) they want approval automated too, eventually, but this specific request is the foundation, not that end state; (b) it should apply generically across all businesses/roles; (c) triggering should be event-driven (task completion), not cron. This ADR builds exactly the queue-population piece of that foundation while deliberately not crossing into removing human approval, which `platform/docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md` explicitly prohibits without its own separate readiness artifact and release gate.

## Benefits

- Removes the single most repetitive piece of manual toil (proposing the obvious next task) without touching the approval gate at all.
- Fixes a real, previously-undiscovered bug that made "operator selection required" false advertising for business-agent scopes.
- Verified safe against unattended execution today: `.github/workflows/*.yml` has no `schedule:` trigger and none references this flow; only `workflow_dispatch`/`push`/`pull_request` exist, all human-initiated, and those only run validation scripts. No daemon/supervisor survived this repo's earlier coordination-layer removal (ADR-0032).
- A second, independent safety backstop exists beyond the approval gate: this repo's runtime state (`platform/system/runtime/*`) is git-tracked, so even a successful auto-trigger chain link that gets activated is inert on a feature branch until a human reviews and merges the PR carrying it — it's not "live" the moment the script runs.

## Drawbacks

- **Single active handoff slot remains a real limitation.** Two independent chains (e.g. two different businesses) completing close together can mean the second only enqueues rather than activates, because only one scope can be "the" current approvable candidate at a time. The anti-clobber guard prevents silently losing an *already-approved* scope, but does not make concurrent chains fully non-interfering. Documented as a Level 2 item in `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`, not solved here.
- **No file locking anywhere in this codebase.** `business_agent_task_queue.py`'s read-modify-write operations (including the new `source` field and auto-generated task IDs) assume a single local process. Fine today; would need addressing before any concurrent/multi-process execution model.
- Two governance docs now both describe autonomy boundaries (`AUTONOMOUS_OPERATIONAL_BASELINE.md` and the new `BUSINESS_AGENT_AUTOMATION_READINESS.md`) — kept consistent by editing the former's "What Remains Disabled" list in the same change, but this is now two places to keep in sync going forward.

## Impact Scope

- New: `platform/system/core/business_agent_trigger.py`, `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`, this ADR.
- Modified (additive): `platform/system/core/agent_role_registry.py` (`next_roles` field + drift-check), `platform/system/core/business_agent_task_queue.py` (`source` field), `platform/system/core/business_agent_handoff.py` (`_request_id` → public `compute_request_id`), `platform/system/core/approved_autonomous_execution.py` (one call site added, gated on `outcome.success`), `platform/app/tools/approval_console_mvp/service.py` (one field's value source changed, `business_role_task` loop only — the pre-existing issue-scope loop is untouched), `platform/docs/current/AUTONOMOUS_OPERATIONAL_BASELINE.md` ("What Remains Disabled" split into population vs. execution).
- Unaffected: the issue/draft repo-dev execution path (`LocalExecutionAdapter`, `agent_issue_bridge.py`), all existing roadmap/frozen-issue-closure governance, `pluggable_provider` roles (still unwired, Stage 4).

## Migration Cost

Low — purely additive to the business-agent path, no schema migration, no data backfill. All existing tests pass unchanged; new tests cover the new behavior.

## Recommendation

Recommend. This is the minimum viable "foundation" the user asked for: it removes real manual toil, fixes a real latent bug along the way, and is verified today to have no path to unattended execution — while explicitly not making the governance-significant decision (removing human approval) that the user said they eventually want but did not ask for in this change.

## Rejected Alternatives

- **Fold the trigger lookup directly into `BusinessAgentExecutionAdapter.run()`** instead of a separate module: rejected because the anti-clobber guard needs to read `agent_handoff/approval.json`, which is an approval-flow concern, not an execution-adapter concern — keeping them separate matches this repo's existing separation between execution (`platform/system/orchestrator/`) and approval (`platform/system/core/agent_execution_approval.py`).
- **A Level-0-4-style elaborate roadmap doc up front**: rejected in favor of only 2 concretely-real levels (0 existing, 1 this build) with Level 2/3 kept as one-line forward-pointers — inventing detailed future levels before they're real would be the kind of premature architecture this repo has already paid down once (ADR-0032).
- **Enqueue-only (no auto-activation) design, requiring a separate explicit "activate" action**: rejected because it would require inventing new console/CLI surface just to make approval possible at all for anything other than whatever's already active, whereas fixing the `handoff_id` bug (already necessary) makes enqueue-and-activate both simpler and correct.
