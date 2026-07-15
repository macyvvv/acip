# AUTONOMOUS_OPERATIONAL_BASELINE

baseline_mode: one_shot_approved_execution_only
one_shot_operational: true
repeated_enabled: false
queue_enabled: false
open_ended_enabled: false
verified_scope_id: DRAFT-OPP-KABUKICHO-001
verified_command: CODEX_EXECUTION_TIMEOUT_SECONDS=300 python3 platform/system/platform/scripts/agent/run_approved_autonomous_execution.py
verified_result: success
release_gate_status: operational_baseline_frozen

