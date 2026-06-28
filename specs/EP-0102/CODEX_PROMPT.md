# Codex Prompt for EP-0102

You are Codex working in the ACIP repository.

## Objective

Read specs/EP-0102/ and implement EP-0102.

## Required Behavior

1. Read all files under specs/EP-0102/.
2. Inspect repository state before editing.
3. Implement only requested files and minimal supporting updates.
4. Do not delete existing implementation files unless explicitly required.
5. Run:
   - python system/scripts/validate_ep_0102.py
   - python system/scripts/validate_ep_0100.py
   - python system/scripts/validate_ep_0101.py
6. Commit:
   - feat: EP-0102 Codex Development Pipeline

## Prohibited

- Runtime external execution
- Platform API mutation
- Auto posting
- Secret use
- Approval bypass
- Deleting agent_system/runtime/**
