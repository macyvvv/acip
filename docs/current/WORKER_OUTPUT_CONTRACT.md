# WORKER_OUTPUT_CONTRACT

task_id: EP-0119
commit_sha: null
worktree_clean: true
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
next_action: Review repository output and continue only after validation passes.
rerun_validation_conditions:
  - Any validation command exits non-zero.
  - Worktree is dirty after an approved execution.
  - Commit SHA is missing after a commit-approved run.
  - Decomposition, routing, or review summary is stale.
