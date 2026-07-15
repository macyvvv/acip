# VALIDATION_STATE

last_validation_status: success
last_validation_command: python scripts/validate_all.py
last_validation_report_json: runtime/validation/validation_report.json
last_validation_report_md: runtime/validation/VALIDATION_REPORT.md
validation_owner: Codex
rerun_required_when:
  - any validation step fails
  - pytest fails
  - runtime validation report is stale
  - validation state does not match repository outputs
human_rerun_policy: Human reruns validation only when repository outputs changed, validation artifacts are stale, or the latest validation failed.
relation_to_worker_output_contract: Validation state is a repository-level summary of validation execution and is referenced by Worker Output Contract as the canonical validation status for review and handoff.
