# ADR-0041: Expand the Interactive Agent Layer for Business, Product, and Legal Work

## Status

Accepted by operator approval on 2026-07-17.

## Context

The `cf_gb_relative_system` WBS review exposed recurring owners that had no corresponding agent: strategy analysis, finance analysis, product management, UX research, application engineering, independent QA, and legal research. Assigning these to the existing six Ops roles would blur real boundaries: MarketingOps is not business strategy, DevOps is not product engineering, SecOps is not legal counsel, and DataOps is not product management.

## Decision

Add three interactive Ops roles and seven interactive specialist roles:

- `businessops`: manages `business-strategy`, `finance-analysis`.
- `productops`: manages `product-management`, `ux-research`, `software-engineering`, `quality-assurance`.
- `legalops`: manages `legal-research`.

Update `opsboard` from six to nine Ops. The interactive layer becomes 9 Ops + 15 specialist agents + opsboard = 25 roles.

Human retains final strategy, approval, capital allocation, legal-risk acceptance, and decisions requiring qualified counsel. The new roles produce evidence, options, implementation, or verification; they do not acquire those authorities.

## Execution Authority

The ten new roles are `.claude/agents/` interactive-session roles only. They are not added to `platform/system/core/agent_role_registry.py`, generated registry JSON, pre-approval policies, schedules, or unattended execution. This avoids silently expanding automation or spend authority.

ADR-0039 remains authoritative for the eight roles that exist in both interactive and automated forms. The seven new specialist roles have no registry-side counterpart. Adding one requires a separate ADR, output contract, prompt/registry definition, policy review, tests, and explicit operator approval.

## Boundaries

- BusinessOps prepares strategy and finance decisions; Human decides.
- ProductOps coordinates product delivery; DevOps owns delivery mechanics, DataOps owns data integrity, SecOps owns security verification, and OpsBoard owns cross-domain readiness synthesis.
- LegalOps performs research and condition tracking; Human or qualified counsel decides legal acceptability. Robots or technical accessibility never substitute for permission.
- QA provides independent product acceptance and does not replace DataOps, SecOps, or DevOps gates.

## Consequences

Benefits:

- Every material WBS responsibility has an explicit owner and supervisor.
- Product implementation no longer leaks into DevOps.
- Legal research no longer leaks into SecOps or an undefined `Legal` label.
- Strategy analysis can be automated interactively without transferring strategic authority.

Costs:

- Ten more role definitions must remain coherent.
- OpsBoard synthesis becomes broader.
- Interactive-only roles cannot be assumed available to unattended Level 3 execution.

## Rejected Alternatives

- Add one Ops role for every WBS label: rejected as fragmented and expensive to coordinate.
- Put strategy/finance under MarketingOps: rejected because growth operations are downstream of business decisions.
- Put engineering/QA under DevOps: rejected because product correctness and delivery mechanics are different responsibilities.
- Put legal research under SecOps: rejected because legal authority, contract interpretation, and security controls are distinct.
- Add all new roles to unattended automation now: rejected as an unapproved authority and execution-surface expansion.

## Validation

- Every new role has a unique frontmatter name and explicit reporting line.
- OpsBoard lists all nine Ops and recognizes the interactive-only boundary.
- WBS tasks resolve to an existing agent or Human.
- Automated registry remains unchanged.
