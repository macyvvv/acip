# TASK_DECOMPOSITION

Task decomposition is deterministic and capability-driven.

## Rule

- accept EP contract text or task payload
- infer capability requirements from objective text or explicit requirements
- generate stable subtask identifiers
- resolve candidate worker through Capability Router
- fail validation if a capability is unsupported

## Output Contract Relation

Task decomposition produces a machine-readable subtask plan that can be summarized into the Worker Output Contract for downstream execution.
