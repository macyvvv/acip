# WORKER_OUTPUT_CONTRACT

task_id: EP-0120
commit_sha: null
worktree_clean: true
status_semantics:
  success:
    meaning: All required work completed and validation passed.
    next_action: Proceed to review or next repository step.
  partial_success:
    meaning: Some work completed, but one or more required outputs remain incomplete.
    next_action: Review incomplete outputs and resolve the remaining scope.
  failure:
    meaning: Required work did not complete or validation failed.
    next_action: Inspect errors, fix the failure, then rerun validation.
  blocked:
    meaning: Execution cannot continue because a dependency, approval, or repository constraint is missing.
    next_action: Resolve the blocking condition before rerunning execution.
  skipped:
    meaning: No execution was performed because the work was not applicable or was intentionally bypassed.
    next_action: Confirm whether the skipped work should remain skipped or be scheduled later.
decomposition_result:
  source: null
  objective: null
  subtasks: []
routing_result:
  worker_name: null
  candidates: []
review_summary:
  status: pending
  notes: []
  meaning: null
  next_action: null
next_action: Review repository output and continue only after validation passes.
rerun_validation_conditions:
  - Any validation command exits non-zero.
  - Worktree is dirty after an approved execution.
  - Commit SHA is missing after a commit-approved run.
  - Decomposition, routing, or review summary is stale.
  - Worker output status is unsupported or ambiguous.
