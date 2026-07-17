---
name: running-business-agent-tasks
description: Runs a business-agent role task (market_research, marketing, doc_creation, analytics, pdca) through acip's real propose-approve-execute-finalize pipeline so its output becomes a traceable execution artifact under platform/system/runtime/business_agents/, instead of ad-hoc chat text. Use this whenever a business-agent role's output must be real and traceable -- before calling finalize_content.py, before flipping any publishing/policy.json entry off dry_run, before real (non-dry-run) posting to X/Threads/note.com, or when asked to "run the marketing/doc_creation/market_research/analytics/pdca role for <business>" for real rather than as an interactive Agent-tool call. Do not use this for interactive-only advisory work (the Ops roles reviewing something, or a quick opinion) -- use the Agent tool directly for that; this skill is specifically for producing a persisted, provenance-tracked artifact.
---

# Running a business-agent task for real

acip has two separate ways to invoke a business-content role:

1. **Interactive `Agent` tool call** (`subagent_type: "marketing"` etc.) -- fast, no
   persisted artifact, fine for advisory/draft work reviewed in the same
   conversation. This is what most of this session's Ops consultations use.
2. **This pipeline** -- slower, produces a real execution artifact at
   `platform/system/runtime/business_agents/<business_id>/<role_id>/<task_id>/latest.{json,md}`
   with `success`, `stdout`, `resolved_model` etc. **Required** before
   `finalize_content.py` will accept the content (it refuses anything without
   a matching artifact showing `success: true`), which in turn is required
   before any real (non-dry-run) publish.

If you've already drafted copy via an interactive Agent call and need it to
become postable, you cannot just hand-copy that text into `finalize_content.py`
-- there is no artifact backing it. Either re-run the work through this
pipeline (feeding the already-reviewed content/constraints as the task
description, as marketingops/marketing already validated it) or accept that
only a human can manually author an artifact (rare, avoid).

## Steps

1. **Check the working tree is clean first.** `run_scheduled_execution.py`
   refuses to run (`working_tree_dirty_skip_wake`) on a dirty tree, including
   files other concurrent sessions/automation may have touched. Run
   `git status --porcelain` and resolve or wait before proceeding -- do not
   force through by committing/discarding files you don't recognize; they
   may belong to another in-progress session.

2. **Check pre-approval coverage** so the task can auto-run without a manual
   `set_execution_approval.py` call:
   ```
   python3 -c "
   import json
   d = json.load(open('platform/system/runtime/agent_handoff/auto_approval_policy.json'))
   for p in d['policies']:
       if p['business_id'] == '<business_id>' and p['role_id'] == '<role_id>':
           print(p)
   "
   ```
   If no matching enabled policy exists, this task needs a manual approval
   step (a human decision, not something to route around) -- surface that to
   the operator rather than proceeding.

3. **Propose the task**:
   ```
   python3 platform/system/scripts/business_agent/propose_task.py \
     --business-id <business_id> \
     --role-id <role_id> \
     --task-id <task-id-unique-per-role> \
     --title "<short title>" \
     --task-description "<the full brief -- be as complete as you would be
       briefing a fresh Agent call: context, constraints, what to avoid,
       what prior artifacts to read first>"
   ```
   This only queues a candidate at
   `platform/system/runtime/agent_handoff/scopes/<business_id>/<role_id>/<task_id>/handoff.json`
   -- nothing runs yet.

4. **Run one scheduled-execution wake**:
   ```
   python3 platform/system/scripts/business_agent/run_scheduled_execution.py
   ```
   This calls the real `claude` CLI headlessly for every eligible candidate
   task (not just the one you just proposed -- other pending candidates may
   also run). Read the printed summary: `executed=N`, `pr_url=`, and any
   `*_skip_reason` fields. A `working_tree_dirty_skip_wake` here (not caught
   at step 1, e.g. another process dirtied the tree in between) means retry
   later, not force through.

5. **Verify the artifact**, don't assume the printed summary is enough:
   ```
   cat platform/system/runtime/business_agents/<business_id>/<role_id>/<task_id>/latest.json
   ```
   Check `"success": true` and that `stdout` is real content, not a CLI
   session/rate-limit notice (`business_agent_execution_adapter.py`'s own
   `_cli_failure_notice()` check exists because exit 0 does not guarantee
   real output).

6. **Only then** hand the exact final text to `finalize_content.py` (see
   that script's own `--help` -- it needs `--business-id --role-id --task-id
   --platform --final-text-file --finalized-by`, and optionally
   `--reply-to` for a reply-chain post). This step is deliberately human-
   curated per that script's own docstring -- do not auto-select which
   candidate line becomes the final text without showing it to the operator
   first if this is going to real, costed, public publication.

7. **Publishing itself** (actually calling e.g. `providers_x.py`) is a
   separate real-money, real-external-effect action -- confirm the relevant
   `publishing/policy.json` entry's `provider` is not `dry_run` before
   expecting a real post, and never flip that off `dry_run` without the
   operator's explicit, current-turn approval (a past approval for a
   different task/business does not carry over).

## Common failure modes

- **Dirty working tree**: see step 1. Do not `git add -A` / `git stash` other
  sessions' in-progress files to force a clean state -- ask the operator, or
  wait.
- **No pre-approval policy for this business/role pair**: this is a real gate,
  not a bug -- a human must either author a `PREAPP-*` policy entry or run
  the manual approval script. Do not treat the absence as something to code
  around.
- **`dry_run` publishing provider**: producing a finalized artifact does NOT
  mean it gets posted -- confirm the policy's `provider` field and the
  operator's explicit approval before assuming anything went out for real.
