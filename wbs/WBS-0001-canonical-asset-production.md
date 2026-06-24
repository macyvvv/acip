# WBS-0001: Canonical Asset Production

## Conclusion

This WBS defines the execution sequence for creating the first repository-canonical asset.

## Current Phase

Knowledge Factory

## Current Objective

Canonical Asset Production

## Scope

In scope:

- define asset structure
- define quality gate
- create asset and review templates
- validate required repository files
- produce first canonical asset after approval

Out of scope:

- runtime implementation
- auto posting
- platform API integration
- scraping-dependent workflows
- new application frameworks

## Work Packages

| ID | Work Package | Owner | Output | Done Condition |
|---|---|---|---|---|
| WBS-01 | Add canonical asset basis files | Codex | `basis/008`, `009`, `010` | Files merged |
| WBS-02 | Add ADR | ChatGPT / Codex | `ADR-0003` | ADR reviewed |
| WBS-03 | Add templates | Codex | asset and review templates | Templates merged |
| WBS-04 | Add issue templates | Codex | GitHub issue templates | Templates available |
| WBS-05 | Add validation | Codex | script and workflow | CI passes |
| WBS-06 | Select first asset | Human / ChatGPT | target asset issue | Human approved |
| WBS-07 | Draft first asset | ChatGPT / Codex | asset markdown file | Review ready |
| WBS-08 | Review first asset | ChatGPT / Codex | review notes | Gate pass or revision |
| WBS-09 | Approve first asset | Human | approval comment | Approved |
| WBS-10 | Merge first asset | Codex | merged PR | Asset canonical |

## Milestones

| Milestone | Done Condition |
|---|---|
| M1: Production System Ready | validation passes |
| M2: First Asset Selected | issue approved |
| M3: First Asset Canonical | PR merged |

## Risks

| Risk | Mitigation |
|---|---|
| Asset scope expands during production | enforce template scope / out-of-scope |
| Chat output treated as canonical | repository merge rule |
| Platform output created too early | prohibit platform-specific production until source asset approved |
| Runtime automation leakage | validation and phase prohibitions |
