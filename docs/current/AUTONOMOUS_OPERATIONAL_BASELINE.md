# AUTONOMOUS_OPERATIONAL_BASELINE

## Summary
The operational baseline for autonomy is one-shot approved execution only.

## What Is Operational
- Approved handoff
- Execution-ready bridge
- One-shot autonomous execution

## What Remains Disabled
- Repeated autonomy
- Queue autonomy
- Open-ended autonomy

## Canonical Verified Example
- Scope: `DRAFT-OPP-KABUKICHO-001`
- Command:
```bash
CODEX_EXECUTION_TIMEOUT_SECONDS=300 python3 system/scripts/agent/run_approved_autonomous_execution.py
```
- Result: `success`
- Stop reason: `completion_marker_written`

## Operator Rule
Default operating mode for autonomy is one-shot approved execution only.

## Prohibition
No new autonomy layer may be enabled unless a new readiness artifact and release gate are added first.

