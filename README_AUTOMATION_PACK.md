# ACIP Automation Pack

## Conclusion

This pack adds the minimum files needed to close GitHub foundation automation without starting runtime automation.

## Files

```text
docs/GITHUB_FOUNDATION_CHECKLIST.md
basis/007_automation_scope.md
adr/ADR-0002-foundation-automation.md
scripts/validate_foundation.py
.github/workflows/foundation-check.yml
.github/ISSUE_TEMPLATE/foundation_completion.yml
```

## Apply

Copy these files into the ACIP repository root.

Then run:

```bash
python scripts/validate_foundation.py
```

If validation passes, create a branch and PR.

## Done Condition

- local validation passes
- GitHub Actions validation passes
- Human approves PR
- PR merges into `main`

## Non-goal

This pack does not implement runtime automation, auto posting, platform API integration, or scraping.
