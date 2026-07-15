# REVIEW_OUTPUT_INTEGRATION

Review output integration keeps decomposition, routing, review, and worker output aligned.

## Responsibilities

- accept a task decomposition result
- accept a capability routing result
- produce a deterministic review summary
- expose worker output fields for subtask-level reporting

## Contract Relation

The integration layer bridges `TaskDecomposer`, `CapabilityRouter`, `ExecutionKernel`, and `WORKER_OUTPUT_CONTRACT`.
