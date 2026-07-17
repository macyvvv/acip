# ONE_SHOT_APPROVED_AUTONOMOUS_EXECUTION

## Purpose
Allow one explicitly approved autonomous handoff to trigger exactly one bounded execution run through the existing repository execution flow.

## What Is Automated Now
- Approved handoff evaluation
- One-shot execution trigger for one explicit scope
- Canonical runtime recording of the execution result

## What Still Requires Human Approval
- Approval artifact creation
- Approval state changes
- Any future live-execution enablement

## Exact Command
```bash
python3 platform/system/scripts/agent/run_approved_autonomous_execution.py
```

## Stop Conditions
- approval missing
- approval stale or superseded
- blocked thread
- completion marker written
- execution failure
- one execution per invocation

## Kill Switch Behavior
The command stops after one bounded run and never retries, loops, or selects a second issue.

## Still Explicitly Forbidden
- automatic `run_until_idle`
- supervisor bypass
- open-ended autonomy
- implicit approval
- GitHub mutation outside current governance
- daemonization

