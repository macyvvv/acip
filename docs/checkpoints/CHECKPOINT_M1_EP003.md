# CHECKPOINT_M1_EP003

Version: v1.0
Status: Candidate Canonical

---

# 1. Repository Context

GitHub Account: macyvvv  
Repository: acip  
Branch: main  

---

# 2. Current Phase

Repository Operationalization

---

# 3. Current Objective

Checkpoint運用をRepository上の標準Workerとして定着させる。

---

# 4. Completed

以下をRepositoryへ配置済み。

.system/prompts/codex/CHECKPOINT_WORKER.md

このWorker Promptは、ChatGPTが生成したCheckpoint文書をCodexがRepositoryへ同期するための標準手順である。

---

# 5. Worker Responsibility

Human:
- Approve
- Review
- Push
- Final Decision

ChatGPT:
- Checkpoint content generation
- Review
- Canonical/Draft classification

Codex:
- Create or update files
- Preserve markdown
- Run git status
- Run git diff
- Report unexpected changes

---

# 6. Operating Rule

Checkpoint更新は以下の順で行う。

1. ChatGPT creates checkpoint content.
2. Human approves content.
3. Codex writes file to repository.
4. Codex shows git status and diff.
5. Human reviews and pushes.
6. ChatGPT verifies repository state.

---

# 7. Current WBS

M1 First Revenue

EP-001 Scout / Market Selection
Status: Done

EP-002 Canonical Asset Production
Status: Doing

Repository Operationalization
Status: Done

---

# 8. Canonical

以下をCanonicalとして採用する。

- Current Repository: macyvvv/acip
- Current Branch: main
- Checkpoint path: docs/checkpoints/
- Codex checkpoint worker path: .system/prompts/codex/CHECKPOINT_WORKER.md
- Checkpoint synchronization procedure

---

# 9. Draft

以下はDraftとする。

- CA-0001〜CA-0020
- CA-0021〜CA-0100
- Publishing workflow
- KPI review workflow

---

# 10. Next

EP-002に戻る。

Next Task:
Canonical Asset CA-0001〜CA-0020をPublish Ready品質へ引き上げる。

Done:
20件が投稿可能な形式となり、HumanがGo/No-Goだけ判断できる状態になること。
