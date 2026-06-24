# 091 Agent Runtime MVP Policy

## Conclusion

Agent Runtime MVP may execute local dry-run planning only.

## Allowed

- repository read
- graph read
- context pack read
- runtime context generation
- plan generation
- queue item generation
- review summary generation
- approval gate generation

## Prohibited

- external API mutation
- auto posting
- scraping-dependent automation
- secret use
- approval bypass

## Repository Rule

Repository overrides conversation.
