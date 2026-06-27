# Codex Execution Prompt

Request ID: REQ-PLANNED-0001
Request Status: ready
Objective: Constitution v3 Freeze
Selected Work Item: None

Implement Issue #28 / ACCEPTANCE-0001 using repository artifacts only.
Read runtime/planning/latest.json, runtime/repository_state/latest.json, runtime/work_planner/latest.json, and runtime/request/execution_request.json.
Run:
- python3 scripts/validate_all.py
- python3 -m pytest -q
- git status

Do not auto-push.
Do not modify Repository OS architecture.
