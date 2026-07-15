# CONTENT_PIPELINE

Version: v1.0

Status: Canonical

---

# Purpose

ConversationからRepositoryへKnowledge Assetを変換し、
Publish・Review・改善を再現可能な形で実行する。

---

# Principle

Conversationは一時情報である。

RepositoryをSingle Source of Truthとする。

Current Objectiveを途中で変更しない。

Current Task完了まで新Taskを開始しない。

---

# Pipeline

Question

↓

Canonical Asset

↓

Repository Draft

↓

Repository Review

↓

Publish

↓

KPI Review

↓

Wisdom Update

---

# Worker

## Human

Responsibility

- Mission
- Priority
- Approval
- Publish
- Final Decision

Never

- Copy implementation
- Manual synchronization
- Architecture refactoring during Execution

---

## ChatGPT

Responsibility

- Strategy
- Documentation
- Canonical Asset generation
- Review
- Self criticism

Never

- Change Current Objective
- Modify approved architecture
- Skip Definition of Done

---

## Codex

Responsibility

- Repository synchronization
- Markdown creation
- Directory creation
- Implementation

Never

- Redesign architecture
- Rename directories
- Modify unrelated files

---

# Workflow

## STEP 1

Artifact

Canonical Asset Draft

Owner

ChatGPT

Done

Question

Answer

Evidence

Wisdom

CTA

completed.

---

## STEP 2

Artifact

platform/knowledge/draft/CA-XXXX.md

Owner

Codex

Done

Markdown synchronized.

UTF-8 preserved.

Unexpected diff does not exist.

---

## STEP 3

Artifact

Repository Review

Owner

ChatGPT

Done

Repository state reviewed.

Structure validated.

Current Objective unchanged.

---

## STEP 4

Artifact

Publish Decision

Owner

Human

Done

Go

or

No-Go

decided.

---

## STEP 5

Artifact

Published View

Owner

Codex

Done

Published artifact generated.

Repository synchronized.

---

## STEP 6

Artifact

KPI Review

Owner

ChatGPT

Done

Learning extracted.

Improvement proposal created.

Question Score updated.

---

# Artifact Lifecycle

Question

↓

Draft

↓

Canonical

↓

Published

↓

Wisdom

---

# Repository

platform/knowledge/

draft/

canonical/

published/

questions/

---

# Validation

Every execution must confirm

Current Objective

Current Task

Current Artifact

Current Owner

Definition of Done

before starting work.

---

# Stop Rule

Stop execution immediately if

Current Objective changes,

Architecture changes,

Repository structure changes,

or Human approval is required.

---

# Success Criteria

Conversation alone is never the source of truth.

Repository always contains the latest approved artifact.

Every artifact has

Owner

Definition of Done

Review path

Repository path.

Execution is reproducible by another Worker without additional explanation.