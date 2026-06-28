# EP-0104 Manifest

## EP

- id: EP-0104
- name: Executable Specification Foundation
- type: process / tooling
- phase: Autonomous Engineering Transition
- objective: Executable Specification Foundation

## Required Outputs

Codex must create or update:

- `specs/schema/ep_contract.schema.json`
- `specs/templates/ep_contract.template.yaml`
- `specs/EP-0104/ep_contract.yaml`
- `system/scripts/specs/validate_ep_contract.py`
- `system/scripts/specs/load_active_ep_contract.py`
- `system/scripts/validate_ep_0104.py`
- `.github/workflows/ep0104-executable-specification.yml`
- `README_EP0104_EXECUTABLE_SPECIFICATION.md`

## Done Condition

`python system/scripts/validate_ep_0104.py` passes, followed by EP-0103, EP-0102, EP-0101, and EP-0100 regression validation.
