# 072 Agent Orchestrator Policy

## Conclusion

The Agent Orchestrator coordinates ChatGPT, Codex, validation scripts, GitHub Actions, and future approved agents through repository-derived context.

## Purpose

The orchestrator converts Repository Graph and Agent Context Pack into bounded execution plans.

## Responsibilities

- resolve current objective
- load repository graph
- build context bundle
- route tasks to the correct actor
- define validation
- preserve Human Boundary
- preserve Runtime Boundary
- generate review-ready status

## Human Boundary

Human handles Mission, Approval, Emergency Stop, Risk Acceptance, Capital Allocation, and Runtime Transition Approval.

## Runtime Boundary

The orchestrator must not perform autonomous external actions, platform API mutation, auto posting, scraping-dependent automation, or secret use until explicitly approved.

## Repository Rule

Repository overrides conversation.
