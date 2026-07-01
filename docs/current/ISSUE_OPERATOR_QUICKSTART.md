# ISSUE_OPERATOR_QUICKSTART

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
- `system/runtime/issues/completed/issue_*.json`

## Confirm Completion
- Verify the issue has a completion marker in `system/runtime/issues/completed/`.
- Verify the latest completion marker in `system/runtime/handoff/completion/latest.json`.

## Identify Failure
- Check `system/runtime/local_execution/latest.json` for failure reasons.
- Check `system/runtime/supervisor/latest.json` for selection and status.
- Check `system/runtime/github/open_issues.json` to confirm the issue is still open or removed.
