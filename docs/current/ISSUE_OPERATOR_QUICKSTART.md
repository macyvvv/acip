# ISSUE_OPERATOR_QUICKSTART

## Approval Console MVP
Canonical entrypoint for one-shot approved execution:
```bash
python3 system/scripts/agent/run_approval_console.py
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

## Run the Loop
1. Sync open issues:
```bash
python3 system/scripts/sync_github_issues.py
```
2. Run the supervisor / issue loop:
```bash
./system/scripts/run_until_idle.sh
```

## Inspect After Execution
- `system/runtime/github/open_issues.json`
- `system/runtime/supervisor/latest.json`
- `system/runtime/local_execution/latest.json`
- `system/runtime/handoff/latest.json`
- `system/runtime/handoff/completion/latest.json`
- `system/runtime/roadmap/issue_portfolio.json`
- `system/runtime/issues/completed/issue_*.json`

## Confirm Completion
- Verify the issue has a completion marker in `system/runtime/issues/completed/`.
- Verify the latest completion marker in `system/runtime/handoff/completion/latest.json`.

## Identify Failure
- Check `system/runtime/local_execution/latest.json` for failure reasons.
- Check `system/runtime/supervisor/latest.json` for selection and status.
- Check `system/runtime/github/open_issues.json` to confirm the issue is still open or removed.
