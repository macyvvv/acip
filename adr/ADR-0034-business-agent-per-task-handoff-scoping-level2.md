# ADR-0034: Business Agent Platform Level 2 — Per-Task Handoff Scoping and Concurrency

## Status

Accepted

## Current Design (superseded)

ADR-0033 (Level 1) gave the business agent platform automatic next-task proposal, but every business_role_task scope — from any business, any role — still shared a single, repo-wide handoff/approval slot (`system/runtime/agent_handoff/latest.json` / `approval.json`), the same one the pre-existing issue/draft repo-dev flow uses. Only one scope could be "the" currently-approvable candidate at a time. Level 1's `business_agent_trigger.py` worked around this with an anti-clobber guard (skip activation if a different, currently-approved-and-pending scope existed), and `ApprovalConsoleService`/`propose_task.py` inherited the same single-slot assumption — `propose_task.py` had no guard at all, silently overwriting whatever was pending. A shared `system/runtime/agent_execution/latest.json` had the same problem for execution results.

## Proposed Design (adopted)

Each `(business_id, role_id, task_id)` scope gets its own handoff/approval/execution-result files, mirroring the existing per-task artifact directory convention (`system/runtime/business_agents/{business_id}/{role_id}/{task_id}/`):

- `system/runtime/agent_handoff/scopes/{business_id}/{role_id}/{task_id}/{handoff,approval}.json` — `system/core/business_agent_handoff.py::scope_dir()`/`write_business_agent_handoff()`/`load_business_agent_handoff()`.
- `system/runtime/agent_execution/scopes/{business_id}/{role_id}/{task_id}/latest.json` — `ApprovedAutonomousExecution._write_runtime()` branches on whether the handoff carries `business_id`/`role_id`.
- New `system/core/agent_execution_approval.py::evaluate_business_agent_scope_approval(business_id, role_id, task_id, base_path)`, sharing its field-matching validation with the unchanged `evaluate_execution_approval()` via an extracted private helper.
- `ApprovedAutonomousExecution.run()` gains optional `business_id`/`role_id`/`task_id` kwargs; `run_approved_autonomous_execution.py` gains matching `--business-id`/`--role-id`/`--task-id` CLI flags. Omitted, behavior is unchanged (top-level path, issue/draft only).
- `set_execution_approval.py` parses `business_id`/`role_id`/`task_id` out of `--scope-id` when `--scope-type business_role_task` and writes to that scope's own approval file.
- `business_agent_trigger.py`'s anti-clobber guard is **deleted, not adjusted** — with per-task files, two different scopes never share a path, so there is nothing to clobber. This also closes the PDCA loop (`pdca`'s `next_roles` now includes `market_research`), previously left open specifically because closing it under the old single-slot design would have meant a business's own PDCA cycle serializing against its own content chain.
- `ApprovalConsoleService.load_scopes()`'s `business_role_task` loop now looks up each candidate's own approval/execution-result files instead of one shared pair read once per call.
- New `system/core/file_lock.py` (a `fcntl.flock`-based context manager, short timeout, hard error rather than silent retry), applied only to the two files that remain genuinely shared across all businesses: `business_agent_task_queue.py`'s `queue.json` and `kpi_store.py`'s `kpi.json`. Per-task files need no locking — no two processes legitimately touch the same task's file at once.

The top-level `agent_handoff/latest.json`/`approval.json`/`agent_execution/latest.json` are **untouched** and remain exclusively used by the pre-existing issue/draft repo-dev path.

## Reason for Change

Direct operator request, with a concrete stated business reason: site/product businesses (Kabukicho) have little ongoing work once built, while SNS/content businesses (`text_syndicate`, Somia's content cadence) need continuous production — meaning one business's pending review should never block another's chain from progressing. An initial design draft scoped by business only (`agent_handoff/{business_id}/...`); an adversarial design-review pass found that this would still serialize a *single* business's own PDCA loop against its own content chain once the loop closed — exactly the case (`text_syndicate` needing continuous output) motivating this work. Per-task scoping costs about the same amount of code and removes that failure mode entirely rather than narrowing it.

## Benefits

- Two businesses (or two roles within one business) can now have independently-pending, independently-approvable scopes at the same time, with zero risk of one silently overwriting the other's handoff, approval, or execution result.
- Fixes a real, previously-undiscovered bug for free: `propose_task.py` had no anti-clobber protection at all under the old single-slot design.
- Closes the PDCA loop, enabling genuine continuous content/PDCA cycling per business — the actual capability this stage exists to deliver.
- The design-review pass also confirmed (by reading the actual live runtime state) that the one scope pending migration had never been approved, so no human-reviewed approval needed to be carried forward — migration was a pure regenerate-in-place.

## Drawbacks

- Two more shared files (`queue.json`, `kpi.json`) still require locking and are not addressed by per-task scoping; `file_lock.py` covers them, but this remains the one place true contention can still occur.
- File locking here is POSIX-only (`fcntl`); fine given this repo's CI (`ubuntu-latest`) and local dev (macOS) are both POSIX, but would need revisiting if a Windows runner were ever introduced.
- No actual batch/parallel-execute runner was built — "two terminals is safe" is the delivered capability, not "one command runs N scopes concurrently." That remains a stretch goal, not built here.
- The top-level legacy path and the new per-task path are now two parallel handoff mechanisms living side by side, distinguished only by which code path (`evaluate_execution_approval` vs `evaluate_business_agent_scope_approval`) a caller uses. This is intentional (zero risk to the working issue/draft path) but is a real, permanent bit of duplication a future reader needs to understand.

## Impact Scope

- New: `system/core/file_lock.py`, this ADR, and the per-task/per-scope directory trees under `system/runtime/agent_handoff/scopes/` and `system/runtime/agent_execution/scopes/`.
- Modified (additive/parameterized, not rewritten): `system/core/business_agent_handoff.py`, `system/core/agent_execution_approval.py`, `system/core/business_agent_task_queue.py`, `system/core/kpi_store.py`, `system/core/business_agent_trigger.py` (simplified — guard removed), `system/core/agent_role_registry.py` (`pdca.next_roles`), `system/core/approved_autonomous_execution.py`, `system/scripts/agent/set_execution_approval.py`, `system/scripts/agent/run_approved_autonomous_execution.py`, `app/tools/approval_console_mvp/service.py`.
- Unaffected: the issue/draft repo-dev execution path in full (`LocalExecutionAdapter`, `agent_issue_bridge.py`), `pluggable_provider` roles (still unwired, Stage 4), Level 3 (human approval requirement, completely untouched).

## Migration Cost

Low. One live pending scope (`text_syndicate/doc_creation/auto-0001`) existed at the time of this change; it had never been approved, so migration was a single `write_business_agent_handoff()` call at the new location, with the stale top-level `approval.json` (for an unrelated, already-executed `market_research` scope) left alone rather than carried forward.

## Recommendation

Recommend. Directly delivers the stated need (SNS-type businesses aren't blocked by other businesses' pending reviews) without touching the human-approval requirement, and closes a design gap (per-business scoping's same-business PDCA-vs-content collision) that an adversarial review caught before it shipped rather than after.

## Rejected Alternatives

- **Per-business scoping** (`agent_handoff/{business_id}/...`) instead of per-task: rejected after design review found it would still serialize a business's own PDCA loop against its own content chain once the loop closed — the exact scenario this change targets.
- **A single JSON file keyed by scope** (e.g. `agent_handoff/latest.json` becomes `{"business:role:task": {...}, ...}`) instead of a directory tree: rejected because every read/write would still contend on one `flock` over one file, reintroducing exactly the serialization this change exists to remove, even between logically unrelated businesses.
- **`os.O_EXCL` lockfile** instead of `fcntl.flock`: rejected — a lockfile left behind by a killed process becomes a permanent deadlock requiring manual cleanup; `flock` releases automatically on process death.
