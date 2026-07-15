# Codex Execution Prompt

Request ID: REQ-ISSUE-0030
Request Status: ready
Objective: Constitution v3 Freeze
Selected Work Item: Issue #30: PRODUCT-0001: Product Launch Checklist
Selected Issue Number: 30
Selected Issue Title: PRODUCT-0001: Product Launch Checklist

Implement Issue #30 / PRODUCT-0001: Product Launch Checklist using repository artifacts only.
Read platform/system/runtime/planning/latest.json, platform/system/runtime/repository_state/latest.json, platform/system/runtime/work_planner/latest.json, and platform/system/runtime/request/execution_request.json.
Run:
- python3 platform/system/platform/scripts/validate_all.py
- python3 -m pytest -q
- git status

Do not auto-push.
Do not modify Repository OS architecture.
