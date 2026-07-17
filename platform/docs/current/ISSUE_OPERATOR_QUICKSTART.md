# ISSUE_OPERATOR_QUICKSTART

## Approval Console MVP
Canonical entrypoint for one-shot approved execution:
```bash
python3 platform/system/scripts/agent/run_approval_console.py
```

Workflow:
1. Candidate discovery runs first
2. Select exactly one candidate
3. Approve
4. Run one-shot execution
5. Review success / blocked / failure
6. Stop

Boundaries:
- One-shot only
- Repeated autonomy disabled
- Queue autonomy disabled
- Open-ended autonomy disabled
- Human selection still required
- The approval candidates shown here are the one-shot-ready subset of the broader issue portfolio roadmap.

## Create an Issue
1. Open GitHub and create a new issue.
2. Use the repository’s existing issue naming convention.

## Sync Open Issues
```bash
python3 platform/system/scripts/sync_github_issues.py
```
This repo has no continuous/idle-loop runner -- matches the "Repeated
autonomy disabled" boundary stated above. Each execution is one-shot via
the Approval Console (see above); re-run it manually for the next
candidate.

## Inspect After Execution
- `platform/system/runtime/github/open_issues.json`
- `platform/system/runtime/supervisor/latest.json`
- `platform/system/runtime/local_execution/latest.json`
- `platform/system/runtime/handoff/latest.json`
- `platform/system/runtime/handoff/completion/latest.json`
- `platform/system/runtime/roadmap/issue_portfolio.json`
- `platform/system/runtime/issues/completed/issue_*.json`

## Confirm Completion
- Verify the issue has a completion marker in `platform/system/runtime/issues/completed/`.
- Verify the latest completion marker in `platform/system/runtime/handoff/completion/latest.json`.

## Identify Failure
- Check `platform/system/runtime/local_execution/latest.json` for failure reasons.
- Check `platform/system/runtime/supervisor/latest.json` for selection and status.
- Check `platform/system/runtime/github/open_issues.json` to confirm the issue is still open or removed.
