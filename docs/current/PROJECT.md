# PROJECT

## Mission

Build an AI Native Company.

## Vision

Knowledge First

Platform Independent

Human Approval Minimal

GitOps

## Current Phase

Phase 3

Business Agent Automation Platform live (Levels 0-3a/3c) + Governance
Layer Overhaul in progress (`adr/ADR-0037`)

## Current Repository

GitHub

Canonical

## Current Objective

Retire ChatGPT/Codex-era coordination scaffolding and rigid absolute rules
that no longer match how this repo is actually operated (see
`adr/ADR-0037`), while keeping every genuinely enforced or durable safety
property intact: PR-required workflow, human approval gate, Level 3a/3c's
real spend caps, secret-handling discipline.

## Current Priority

1 Governance layer overhaul (in progress)

2 Business agent platform: Level 3b (scheduled/unattended execution) --
not started, requires explicit separate operator sign-off

3 Product surfaces under `app/products/` -- ongoing iteration

## Decision Rule

Global Optimization

over

Local Optimization

Name the real underlying concern (cost, irreversibility, determinism,
secrets) in any new rule, rather than writing an unqualified absolute --
see `adr/ADR-0037` for why this was added as an explicit convention.

## Human Responsibility

Strategy

Approval

Capital Allocation

## Claude Code Responsibility

Architecture

Implementation

Refactoring

Testing

Review

Pull Request authorship

This repo used to split this work between ChatGPT (architecture/review)
and Codex (implementation/PR) because neither tool retained context across
sessions. Claude Code holds a continuous session and executes directly, so
that split is gone -- see `CLAUDE.md`'s "Operating model" section.

## Success KPI

Human Approval Time

< 5 min / day

Knowledge Asset Growth

Continuous

Repository

Canonical

## Next Action

Update automatically when Phase changes.