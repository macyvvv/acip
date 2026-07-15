# BOOT

> Superseded by [CLAUDE.md](../CLAUDE.md) for how Claude should operate in
> this repo. Kept as historical record of the ChatGPT+Codex protocol.

## Purpose

Define the repository boot sequence for ChatGPT, Codex, and future AI agents.

This file is the first runtime instruction file after the ChatGPT Custom Instructions bootloader.

## Boot Order

AI agents must reconstruct context in the following order.

```text
1. platform/docs/current/PROJECT.md
2. platform/docs/current/STATE.md
3. AGENTS.md
4. platform/.platform/system/BOOT.md
5. platform/.platform/system/REVIEW.md
6. platform/.platform/system/DECISION.md
7. platform/.platform/system/STYLE.md
8. platform/basis/
9. platform/adr/
10. Issue
11. PR
12. Conversation
