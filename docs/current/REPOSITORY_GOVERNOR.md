# REPOSITORY_GOVERNOR

The repository governor recommends the next EP candidates from repository state, queue state, validation state, and worker registry inputs.

## Responsibilities

- read repository health and validation state
- read refactoring queue and queue state
- produce deterministic EP recommendations
- classify risk and human approval requirements
- emit machine-readable recommendation artifacts

## Output Relation

Governor output is consumed by the Execution Kernel as a planning hint, not as an execution override.
