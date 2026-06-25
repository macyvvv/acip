# CODEX_OUTPUT_CONTRACT

task_id: EP-0107
commit_sha: null
worktree_clean: true
validation_results:
  - command: python scripts/validate_ep_0107.py
    exit_code: 0
next_action: Review repository output and continue to the next EP only after validation passes.
rerun_validation_conditions:
  - Any validation command exits non-zero.
  - Worktree is dirty after an approved execution.
  - Commit SHA is missing after a commit-approved run.
