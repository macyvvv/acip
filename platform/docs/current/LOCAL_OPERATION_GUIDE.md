# LOCAL_OPERATION_GUIDE

## Objective

Reduce Human operation after Acceptance-0001 by standardizing local runtime operation.

## Reproducible Environment

1. `source .venv/bin/activate`
2. `platform/scripts/bootstrap_dev_env.sh`
3. `platform/scripts/check_repo_os_status.sh`

## Standard Workflow

1. Activate the local virtual environment.
2. Refresh the repository status export.
3. Start the supervisor manually on macOS when execution is needed.
4. Copy only the review block from `runtime/operator_status/latest.md` into ChatGPT when review is needed.

## What Human Still Does

- Starts the macOS supervisor process.
- Approves high-risk changes.
- Copies one concise status block for review.

## What Human No Longer Does

- Reconstructs repository context by hand.
- Copies long task instructions into ChatGPT.
- Invents the next operation from scratch.
