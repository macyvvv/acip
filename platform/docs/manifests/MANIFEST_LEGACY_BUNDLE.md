# Manifest Legacy Bundle

This file consolidates manifest variants.

## platform/docs/manifests/MANIFEST.md

EP-0003

## platform/docs/manifests/MANIFEST_EP0100.md

# EP-0100 Manifest

## EP

- id: EP-0100
- name: Agent Runtime MVP
- phase: Runtime Preparation
- objective: Agent Runtime MVP

## Files

- `agent_runtime/`
- `platform/scripts/agent_runtime/`
- `platform/scripts/validate_ep_0100.py`
- `runtime/AGENT_RUNTIME_MVP_SPEC.md`
- `.github/workflows/ep0100-agent-runtime-mvp.yml`

## Done Condition

`python platform/scripts/validate_ep_0100.py` passes.

## platform/docs/manifests/MANIFEST_EP0100_1.md

# EP-0100.1 Manifest

## EP

- id: EP-0100.1
- name: Agent Runtime MVP Import Fix
- type: patch
- target: EP-0100 Agent Runtime MVP

## Files

- `platform/scripts/agent_runtime/run_dry_run_cycle.py`
- `platform/scripts/agent_runtime/validate_agent_runtime_mvp.py`
- `platform/scripts/validate_ep_0100.py`
- `README_EP0100_1_AGENT_RUNTIME_IMPORT_FIX.md`

## Done Condition

`python platform/scripts/validate_ep_0100.py` passes.

## platform/docs/manifests/MANIFEST_EP0100_2.md

# EP-0100.2 Manifest

## EP

- id: EP-0100.2
- name: Agent Runtime MVP Restore + Import Fix
- type: patch
- target: EP-0100 Agent Runtime MVP

## Done Condition

`python platform/scripts/validate_ep_0100.py` passes.

## platform/docs/manifests/MANIFEST_EP0101.md

# EP-0101 Manifest

## EP

- id: EP-0101
- name: Agent Runtime Task Intake
- phase: Runtime Preparation
- objective: Agent Runtime Task Intake

## Files

- `agent_runtime/task_intake.py`
- `agent_runtime/task_cycle.py`
- `runtime/task_inputs/sample_task.json`
- `platform/scripts/agent_runtime/run_task_intake_cycle.py`
- `platform/scripts/agent_runtime/validate_task_intake.py`
- `platform/scripts/validate_ep_0101.py`

## Done Condition

`python platform/scripts/validate_ep_0101.py` passes.

