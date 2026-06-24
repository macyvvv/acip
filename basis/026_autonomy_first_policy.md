# 026 Autonomy First Policy

## Conclusion

ACIP must prioritize implementation of autonomous operation paths so Human remains focused on Mission, Approval, and Emergency Stop.

## Principle

If a task can be safely performed by ChatGPT, Codex, validation scripts, GitHub Actions, or approved future automation, it should not be assigned to Human by default.

## Human Responsibilities

Human remains responsible for:

- Mission
- Approval
- Emergency Stop
- Risk acceptance
- Capital allocation
- Final strategic judgment

## Non-Human Responsibilities

The following should be delegated where feasible:

- document drafting
- metadata normalization
- validation
- checklist execution
- duplicate detection
- catalog indexing
- registry hygiene
- issue preparation
- PR preparation
- review preparation
- test execution
- status reporting

## Current Boundary

Until runtime implementation is explicitly approved, autonomy is limited to:

- repository-governed documentation
- validation scripts
- GitHub Actions checks
- Codex implementation tasks
- ChatGPT review and prioritization
- issue / PR preparation

## Prohibited Until Approval

- runtime agent execution
- auto posting
- platform API integration
- scraping-dependent automation
- approval bypass
- autonomous external actions

## Design Rule

Every new process document must state which work should be automated or delegated away from Human.
