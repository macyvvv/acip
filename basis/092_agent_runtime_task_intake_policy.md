# 092 Agent Runtime Task Intake Policy

## Conclusion

Agent Runtime may intake repository-defined tasks for dry-run planning only.

## Allowed

- read task JSON
- normalize task
- build plan
- build queue item
- build review summary
- build approval gate

## Prohibited

- external execution
- platform API mutation
- auto posting
- scraping-dependent automation
- secret use
- approval bypass

## Repository Rule

Repository overrides conversation.
