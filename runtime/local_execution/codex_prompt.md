# Codex Execution Prompt

Request ID: REQ-ISSUE-0030
Request Status: ready
Objective: Constitution v3 Freeze
Selected Work Item: Issue #30: PRODUCT-0001: Product Launch Checklist

Implement Issue #28 / ACCEPTANCE-0001 using repository artifacts only.
Read runtime/planning/latest.json, runtime/repository_state/latest.json, runtime/work_planner/latest.json, and runtime/request/execution_request.json.
Run:
- python3 scripts/validate_all.py
- python3 -m pytest -q
- git status

Do not auto-push.
Do not modify Repository OS architecture.
