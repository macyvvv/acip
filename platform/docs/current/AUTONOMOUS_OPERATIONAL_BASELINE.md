# AUTONOMOUS_OPERATIONAL_BASELINE

## Summary
The operational baseline for autonomy is one-shot approved execution only.

## What Is Operational
- Approved handoff
- Execution-ready bridge
- One-shot autonomous execution

## What Remains Disabled
- Repeated autonomy
- Queue autonomy (execution) — a queue candidate never executes without a human explicitly approving that specific scope, every time
- Open-ended autonomy

## What Is Operational (business agent platform, Level 1)
- Queue autonomy (population only) — the next candidate task can be proposed automatically on a prior task's success, per `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`. This never approves or executes anything; it only ever adds a candidate for a human to review. See that doc for the full readiness gate and forbidden list.

## Canonical Verified Example
- Scope: `DRAFT-OPP-KABUKICHO-001`
- Command:
```bash
CODEX_EXECUTION_TIMEOUT_SECONDS=300 python3 platform/system/platform/scripts/agent/run_approved_autonomous_execution.py
```
- Result: `success`
- Stop reason: `completion_marker_written`

## Operator Entry Point
Canonical Approval Console command:
```bash
python3 platform/system/platform/scripts/agent/run_approval_console.py
```

Flow:
1. Candidate discovery runs first
2. Select exactly one candidate
3. Approve
4. Run one-shot execution
5. Review success / blocked / failure
6. Stop

## Operator Rule
Default operating mode for autonomy is one-shot approved execution only.

## Prohibition
No new autonomy layer may be enabled unless a new readiness artifact and release gate are added first.

The business-agent platform's Level 3b (scheduled/unattended execution of
generation-only roles) satisfies this via `platform/adr/ADR-0038-business-agent-level-3b-scheduled-unattended-execution.md`
and its release-gate checklist — see
`platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`'s Level 3b section for
the full readiness artifact. The repo-dev one-shot approval flow described
above in this doc is unaffected.

## Approval Lifecycle

Active approval candidates are limited to scopes in `candidate`, `approved`, `blocked`, or `failed` review states when operator action is still required.

Terminal `completed` and `archived` scopes are removed from the approval candidate view and must not be re-approved.

## Portfolio Rule

The issue portfolio roadmap is the governing superset. `NOW`, `NEXT`, `LATER`, and `FROZEN` are portfolio buckets; the one-shot approval console only surfaces the one-shot-ready subset.
