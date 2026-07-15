# GLOSSARY

## Purpose

Define canonical terminology for ACIP.

All AI agents, humans, and automation must use these definitions.

When multiple interpretations exist, this document is authoritative.

---

# Repository

The canonical source of project knowledge and governance.

Repository > Conversation.

---

# Constitution

The highest-level architectural and governance rules.

Implemented by:

- platform/basis/
- ADR
- platform/docs/current/PROJECT.md

---

# Runtime

Operational behavior executed by AI agents.

Implemented by:

- platform/.platform/system/
- AGENTS.md

---

# Project

Long-term mission, objectives, KPIs, and responsibilities.

Stored in platform/docs/current/PROJECT.md.

---

# State

Current operational status.

Stored in platform/docs/current/STATE.md.

---

# Phase

The highest-level project progress indicator.

Examples:

Phase 0
Phase 1
Phase 2

---

# Milestone

A significant deliverable within a Phase.

---

# Epic

A collection of related Issues.

---

# Issue

A unit of work.

Must have acceptance criteria.

---

# Pull Request (PR)

A proposed repository change.

Repository is updated only after merge.

---

# Canonical

The officially adopted version.

Only merged content is canonical.

---

# Proposal

A suggested improvement.

Not adopted until explicitly approved.

---

# Current Design

The currently adopted architecture.

---

# Proposed Design

A candidate replacement architecture.

---

# Change Control

The process for modifying adopted design.

Required format:

Current Design

Proposed Design

Reason

Benefits

Drawbacks

Impact

Migration Cost

Recommendation

---

# Human

Responsible for:

- strategy
- approval
- capital allocation

---

# ChatGPT

Chief Systems Architect.

Responsible for:

- architecture
- governance
- review
- optimization

---

# Codex

Implementation Agent.

Responsible for:

- implementation
- refactoring
- testing
- pull requests

---

# Approval

Explicit human agreement.

Without approval, adopted design remains active.

---

# Global Optimization

Improvement evaluated from the perspective of the entire system.

Preferred over local optimization.

---

# Local Optimization

Improvement that benefits only part of the system.

Must not be adopted if it degrades global performance.

---

# Repository First

Repository artifacts always take priority over conversation history.

Priority:

platform/docs/current/PROJECT.md

platform/docs/current/STATE.md

AGENTS.md

platform/.platform/system/

platform/basis/

ADR

Issue

PR

Conversation
