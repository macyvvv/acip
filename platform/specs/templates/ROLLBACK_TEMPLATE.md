# ROLLBACK_TEMPLATE

## If Committed

git revert <COMMIT_SHA>

## If Uncommitted

git restore .
git clean -fd
