# 007 Automation Scope

## Conclusion

Phase 0 automation is limited to repository governance validation and GitOps hygiene.

## Approved Automation

The following automation is approved in Phase 0:

- repository structure validation
- required file existence validation
- prohibited runtime file detection
- prohibited keyword detection for Phase 0
- pull request checklist enforcement by template
- GitHub Actions execution of foundation validation

## Prohibited Automation

The following remains prohibited in Phase 0:

- runtime agent execution
- auto posting
- platform API integration
- scraping-dependent workflows
- autonomous external actions
- content publishing
- approval bypass

## Boundary

Automation may check whether the repository is ready.

Automation may not operate ACIP as a runtime business system.

## Done Condition

Phase 0 automation is complete when repository validation runs automatically on pull requests and blocks regressions in the foundation files.
