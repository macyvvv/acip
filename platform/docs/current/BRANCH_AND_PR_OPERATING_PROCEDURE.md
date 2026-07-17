# BRANCH_AND_PR_OPERATING_PROCEDURE

## Canonical Workflow
1. Create a feature branch.
2. Make changes on the feature branch.
3. Commit changes locally.
4. Push the feature branch.
5. Create a pull request.
6. Merge only after review and required checks.

## Required Steps
```bash
git switch -c feature/<short-name>
git add <files>
git commit -m "<message>"
git push -u origin feature/<short-name>
```

## Review Flow
- Open a PR against `main`.
- Wait for required checks and human review.
- Merge through the GitHub PR workflow.

## Main Protection
- Never push directly to `main`.
- If the current branch is `main`, stop and switch to a feature branch before pushing.

## Operator Note
- Use the local push guard and repository hook template to enforce the workflow.
- Activate locally with: `bash platform/system/scripts/git/install_hooks.sh`
