# ORCHESTRATOR ARCHITECTURE

Version: v0.1
Status: Draft

## Purpose

ACIP Orchestratorは、RepositoryをSingle Source of Truthとして読み取り、Current Taskを特定し、適切なWorkerへ処理を渡すための最小実行基盤である。

## Scope

Orchestratorが行うこと。

- CURRENT_STATE.mdを読む
- Current Objective / Current Taskを取得する
- TaskをWorkerへ渡す
- Worker結果を受け取る
- Artifact生成結果をRepositoryへ反映する
- Checkpoint更新対象を生成する
- CURRENT_STATE更新対象を生成する

## Non-Scope

Orchestratorは以下を行わない。

- Missionを変更しない
- Architectureを再設計しない
- Asset本文を創作しない
- Humanの承認を代替しない
- Repository構造を勝手に変更しない
- Publish判断を行わない

## Core Flow

```text
CURRENT_STATE.md
↓
State Reader
↓
Task Queue
↓
Dispatcher
↓
Worker
↓
Result
↓
Repository Sync
↓
Checkpoint Candidate
↓
CURRENT_STATE Candidate