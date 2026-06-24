# 075 Execution Queue Policy

## Conclusion

Execution Queue represents ready work for ChatGPT, Codex, scripts, GitHub Actions, and future approved agents.

## Queue Fields

- task_id
- objective
- owner
- source
- context_bundle
- execution_contract
- validation_command
- status
- done_condition
- escalation_condition

## Status Values

- ready
- executing
- blocked
- review
- done
- parked
- escalated

## Rules

- Queue hygiene should be automated.
- Human only reviews decision items.
- Repository overrides conversation.
