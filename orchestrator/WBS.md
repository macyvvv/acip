# ORCHESTRATOR WBS

Version: v0.1
Status: Draft

## Current Milestone

Automation Foundation

## Current Objective

Humanを転記者から解放し、RepositoryをSingle Source of TruthとするOrchestrator MVPを実装する。

## Definition of Done

Codexが追加設計なしでOrchestrator MVPを実装できること。

MVP完了条件:

- CURRENT_STATE.mdを読み取れる
- Current Next ActionをTask化できる
- TaskのArtifact / Owner / DoDを検証できる
- Worker種別を判定できる
- Codex実行Promptを生成できる
- Repositoryへ無承認で書き込まない

---

# EP-001 Architecture Documents

Status: Doing

## Task 001

Artifact:
orchestrator/ARCHITECTURE.md

Owner:
ChatGPT

Done:
責務・境界・Component・Data Modelが定義されている。

## Task 002

Artifact:
orchestrator/ADR-0001.md

Owner:
ChatGPT

Done:
Stateless Orchestrator / Repository SSOTの意思決定が記録されている。

## Task 003

Artifact:
orchestrator/WBS.md

Owner:
ChatGPT

Done:
Codexが実装順序を理解できる。

---

# EP-002 State Reader

Status: Backlog

## Task 001

Artifact:
orchestrator/state.py

Owner:
Codex

Done:
docs/current/CURRENT_STATE.md を読み込める。

## Task 002

Artifact:
State dataclass

Owner:
Codex

Done:
repository / branch / current_phase / current_objective / current_task / next_action を保持できる。

## Task 003

Artifact:
tests/test_state.py

Owner:
Codex

Done:
CURRENT_STATE.md のfixtureからStateを生成できる。

---

# EP-003 Task Queue

Status: Backlog

## Task 001

Artifact:
orchestrator/queue.py

Owner:
Codex

Done:
StateからTaskを生成できる。

## Task 002

Artifact:
Task dataclass

Owner:
Codex

Done:
id / artifact / owner / instruction / done_conditions / target_paths を保持できる。

## Task 003

Artifact:
Task validation

Owner:
Codex

Done:
Artifact / Owner / DoD が欠けたTaskをRejectできる。

---

# EP-004 Worker Interface

Status: Backlog

## Task 001

Artifact:
orchestrator/worker.py

Owner:
Codex

Done:
Worker base classが定義されている。

## Task 002

Artifact:
orchestrator/result.py

Owner:
Codex

Done:
Result dataclassが定義されている。

---

# EP-005 Dispatcher

Status: Backlog

## Task 001

Artifact:
orchestrator/dispatcher.py

Owner:
Codex

Done:
Task Ownerに応じてWorkerを選択できる。

## Task 002

Artifact:
Dispatcher result handling

Owner:
Codex

Done:
Worker Resultを受け取り、review_notes / errors / next_task を表示できる。

---

# EP-006 Codex Prompt Generator

Status: Backlog

## Task 001

Artifact:
orchestrator/workers/codex_worker.py

Owner:
Codex

Done:
Codex用Promptを生成できる。

## Task 002

Artifact:
Prompt template

Owner:
Codex

Done:
対象ファイル・作業内容・DoD・検証コマンドを含むPromptを生成できる。

---

# EP-007 GitHub Worker Stub

Status: Backlog

## Task 001

Artifact:
orchestrator/workers/github_worker.py

Owner:
Codex

Done:
MVPではdry-runのみ実装する。

## Task 002

Artifact:
GitHub write guard

Owner:
Codex

Done:
Human approvalなしでは書き込まない。

---

# EP-008 CLI

Status: Backlog

## Task 001

Artifact:
orchestrator/main.py

Owner:
Codex

Done:
CLIでCurrent Taskを表示できる。

Command:

```bash
python orchestrator/main.py status
