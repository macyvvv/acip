from __future__ import annotations

import json
from pathlib import Path
import shlex
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]


def _load() -> tuple[dict[str, Any], dict[str, Any]]:
    schema = json.loads((ROOT / "task_manifest.schema.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "task_manifest.yaml").read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema)
    return schema, manifest


def validate() -> dict[str, Any]:
    _, manifest = _load()
    tasks = manifest["tasks"]
    ids = [task["id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate task IDs")

    by_id = {task["id"]: task for task in tasks}
    agent_names = {
        line.split(":", 1)[1].strip()
        for path in (REPO_ROOT / ".claude/agents").glob("*.md")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("name:")
    }
    unknown_executors = sorted(
        (task["id"], task["executor"])
        for task in tasks
        if task["executor"] not in agent_names
    )
    if unknown_executors:
        raise ValueError(f"unknown executors: {unknown_executors}")
    missing = sorted(
        (task["id"], dependency)
        for task in tasks
        for dependency in task["depends"]
        if dependency not in by_id
    )
    if missing:
        raise ValueError(f"undefined dependencies: {missing}")

    missing_next = sorted(
        (task["id"], next_id)
        for task in tasks
        for next_id in task["next"]
        if next_id not in by_id
    )
    if missing_next:
        raise ValueError(f"undefined next tasks: {missing_next}")

    inconsistent_handoffs = sorted(
        (task["id"], next_id)
        for task in tasks
        for next_id in task["next"]
        if task["id"] not in by_id[next_id]["depends"]
    )
    if inconsistent_handoffs:
        raise ValueError(f"next/dependency mismatch: {inconsistent_handoffs}")

    visit_state: dict[str, int] = {}

    def visit(task_id: str, path: list[str]) -> None:
        state = visit_state.get(task_id, 0)
        if state == 2:
            return
        if state == 1:
            raise ValueError(f"dependency cycle: {path + [task_id]}")
        visit_state[task_id] = 1
        for dependency in by_id[task_id]["depends"]:
            visit(dependency, path + [task_id])
        visit_state[task_id] = 2

    for task_id in ids:
        visit(task_id, [])

    for task in tasks:
        dependencies = [by_id[item] for item in task["depends"]]
        if task["state"] == "ready" and any(item["state"] != "succeeded" for item in dependencies):
            raise ValueError(f"ready task has incomplete dependency: {task['id']}")
        if task["state"] == "blocked" and not task["depends"]:
            raise ValueError(f"blocked task has no dependency: {task['id']}")
        if task["state"] in {"ready", "succeeded"}:
            for field in ("input_schema", "output_schema", "statistical_method"):
                if not task.get(field):
                    raise ValueError(f"{task['id']} missing {field}")
            if not task["acceptance"]["commands"]:
                raise ValueError(f"{task['id']} has no deterministic acceptance command")
        if task["state"] == "ready":
            execution = task["execution"]
            if execution["kind"] == "command":
                parts = shlex.split(execution["command"])
                if len(parts) < 2 or parts[0] != "python" or not (REPO_ROOT / parts[1]).is_file():
                    raise ValueError(f"ready command does not resolve: {task['id']}")
            elif execution["kind"] == "interactive_agent":
                workflow = execution.get("workflow", "")
                if not workflow.startswith(f"{task['executor']}:"):
                    raise ValueError(f"interactive workflow/executor mismatch: {task['id']}")
            else:
                raise ValueError(f"ready task has unavailable execution kind: {task['id']}")
        if task["state"] == "succeeded":
            for target in task["targets"]:
                if target.endswith("/"):
                    continue
                path = Path(target)
                if target.startswith(("businesses/", "platform/", ".github/")):
                    resolved = REPO_ROOT / path
                else:
                    resolved = ROOT / path
                if not resolved.exists():
                    raise ValueError(f"succeeded task target missing: {task['id']} -> {target}")

    return {
        "task_count": len(tasks),
        "ready": sorted(task["id"] for task in tasks if task["state"] == "ready"),
        "succeeded": sorted(task["id"] for task in tasks if task["state"] == "succeeded"),
    }


if __name__ == "__main__":
    result = validate()
    print(
        "manifest valid: "
        f"tasks={result['task_count']} "
        f"ready={result['ready']} "
        f"succeeded={result['succeeded']}"
    )
