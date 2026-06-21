# BOOT

## Purpose

Define the repository boot sequence for ChatGPT, Codex, and future AI agents.

This file is the first runtime instruction file after the ChatGPT Custom Instructions bootloader.

## Boot Order

AI agents must reconstruct context in the following order.

```text
1. PROJECT.md
2. STATE.md
3. AGENTS.md
4. .system/BOOT.md
5. .system/REVIEW.md
6. .system/DECISION.md
7. .system/STYLE.md
8. basis/
9. adr/
10. Issue
11. PR
12. Conversation