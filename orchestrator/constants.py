from __future__ import annotations

from dataclasses import dataclass

CURRENT_STATE_PATH = "docs/current/CURRENT_STATE.md"
QUEUE_STATE_PATH = "docs/current/QUEUE_STATE.md"
WORKER_STATE_PATH = "docs/current/WORKER_STATE.md"
ARCHITECTURE_PATH = "orchestrator/ARCHITECTURE.md"
ADR_PATH = "orchestrator/ADR-0001.md"
WBS_PATH = "orchestrator/WBS.md"
REPOSITORY_CONVENTIONS_PATH = "basis/REPOSITORY_CONVENTIONS.md"

CHECKPOINT_WORKER = ".system/prompts/codex/CHECKPOINT_WORKER.md"
ASSET_WORKER = ".system/prompts/codex/ASSET_WORKER.md"

WORKER_CEDEX = "Codex"
WORKER_CHATGPT = "ChatGPT"
WORKER_HUMAN = "Human"


@dataclass(frozen=True)
class RepositoryPaths:
    repository_conventions: str = REPOSITORY_CONVENTIONS_PATH
    current_state: str = CURRENT_STATE_PATH
    architecture: str = ARCHITECTURE_PATH
    adr: str = ADR_PATH
    wbs: str = WBS_PATH
