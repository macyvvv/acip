# DECISION

## Purpose

Define how design changes and improvement proposals must be presented.

## Default Rule

Adopted design remains active until a new design is explicitly approved.

Do not silently replace an adopted design.

## When To Propose Change

Propose a change when:

- a more globally optimal solution exists
- current design creates operational risk
- current design creates maintainability risk
- current design causes duplicated responsibility
- current design is not testable
- current design conflicts with repository state
- current design creates unnecessary human workload

## Required Change Proposal Format

Every change proposal must include:

### Current Design

Describe the currently adopted design.

### Proposed Design

Describe the proposed design.

### Reason for Change

Explain why the change is needed.

### Benefits

List expected benefits.

### Drawbacks

List expected drawbacks.

### Impact Scope

List affected files, workflows, agents, users, and phases.

### Migration Cost

Estimate low / medium / high.

### Recommendation

Use one of:

- Strongly recommend
- Recommend
- Optional
- Do not recommend

## Approval Rule

Until the human approves the proposed change, continue using the current design.

## ADR Rule

If the change affects architecture, governance, responsibility, workflow, data model, or runtime behavior, create or update an ADR.

## Rejected Alternatives

For important decisions, record at least one rejected alternative and why it was rejected.