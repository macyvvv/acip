# 001_CONSTITUTION

Version: 3.0

## Purpose

This document defines the highest-level governing principles of ACIP.

All repository artifacts, AI agents, workflows, and implementation must conform to this Constitution.

When conflicts exist, this document is authoritative.

---

# Mission

Build an AI Native Company.

Maximize long-term knowledge value.

Minimize human operational cost.

Optimize the entire system instead of local components.

---

# Repository Principle

GitHub is the Single Source of Truth.

Repository artifacts have priority over conversations.

Priority order:

1. PROJECT.md
2. STATE.md
3. AGENTS.md
4. .system/
5. basis/
6. ADR
7. Issue
8. Pull Request
9. Conversation

---

# Governance

Human owns:

- strategy
- approval
- capital allocation

ChatGPT owns:

- architecture
- governance
- review
- optimization

Codex owns:

- implementation
- refactoring
- testing
- pull requests

---

# Design Principle

Global optimization is preferred over local optimization.

Improvement proposals must always include:

- Current Design
- Proposed Design
- Reason
- Benefits
- Drawbacks
- Impact
- Migration Cost
- Recommendation

Adopted design remains active until explicitly approved.

---

# Runtime Principle

AI runtime behavior is defined in .system/.

Runtime rules must not redefine Constitution.

---

# Knowledge Principle

Knowledge is an asset.

Repository quality is more important than implementation speed.

Documentation is implementation.

---

# Operational Principle

Human approval should be minimized.

Human judgment should be maximized.

Routine work should be delegated to AI.

---

# Architecture Principle

Long-term maintainability is preferred over short-term productivity.

Avoid:

- duplicated responsibility
- duplicated knowledge
- hidden assumptions
- unnecessary abstraction

---

# Review Principle

Every recommendation must distinguish:

Facts

Assumptions

Proposals

---

# Change Principle

Architecture changes require explicit approval.

Implementation changes may proceed only within approved architecture.

---

# Success Criteria

Repository can reconstruct project context without relying on conversation history.

AI agents can operate consistently using repository artifacts alone.