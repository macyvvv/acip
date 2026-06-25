# EXECUTION_KERNEL

The Execution Kernel is the thin orchestration layer that composes Planner, Queue, Dispatcher, Autonomous Loop, and Validation Orchestrator.

## Responsibilities

- load repository context
- read queue state
- produce planner decisions
- execute the default autonomous planning cycle
- resolve worker assignment
- execute one autonomous cycle
- execute validation pipeline
- return machine-readable kernel results

## Output Contract Relation

The kernel produces execution results that can be summarized into the Worker Output Contract and Validation State without duplicating business logic.
