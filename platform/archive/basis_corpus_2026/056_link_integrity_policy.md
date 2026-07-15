# 056 Link Integrity Policy

## Conclusion

Repository links must be auditable so ADR, WBS, policy, runbook, and template chains remain navigable.

## Required Link Types

- ADR to policy or WBS
- WBS to Current Objective
- runbook to objective or validation
- README to validation
- workflow to validation script

## Rule

Broken internal markdown links and missing validation targets must fail Self Test.
